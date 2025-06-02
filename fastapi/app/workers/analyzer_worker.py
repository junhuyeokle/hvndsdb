import asyncio
import os
import uuid

from fastapi.logger import logger
from utils.envs import TEMP
from managers import deblur_gs_manager, unity_manager
from managers import analyzer_manager
from utils.s3 import (
    download_file_from_presigned_url,
    download_folder_from_presigned_url,
    get_last_modified,
    get_presigned_download_url,
    get_presigned_upload_url,
    is_key_exists,
    upload_folder_to_presigned_url,
)
from workers import colmap_worker, frames_worker


async def run(building_id: str):
    FRAMES = not is_key_exists(os.path.join(building_id, "frames.zip"))
    COLMAP = not is_key_exists(os.path.join(building_id, "colmap.zip"))

    sample_path = os.path.join(TEMP, building_id, "sample.mp4")
    colmap_path = os.path.join(TEMP, building_id, "colmap")
    frames_path = os.path.join(TEMP, building_id, "frames")

    logger.info(
        "\n".join(
            [
                sample_path,
                colmap_path,
                frames_path,
                building_id,
            ]
        )
    )

    if FRAMES:
        await download_file_from_presigned_url(
            get_presigned_download_url(building_id + "/sample.mp4"),
            sample_path,
        )

        if not await frames_worker.run(sample_path, frames_path, building_id):
            await upload_folder_to_presigned_url(
                get_presigned_upload_url(
                    building_id + "/frames.zip",
                    "application/zip",
                ),
                frames_path,
            )
        else:
            await analyzer_manager.update_progress(
                building_id, "Frames extraction failed."
            )
            return

    if COLMAP:
        if not FRAMES:
            await download_folder_from_presigned_url(
                get_presigned_download_url(building_id + "/frames.zip"),
                frames_path,
            )

        if not await colmap_worker.run(colmap_path, frames_path, building_id):
            await upload_folder_to_presigned_url(
                get_presigned_upload_url(
                    building_id + "/colmap.zip",
                    "application/zip",
                ),
                colmap_path,
            )
        else:
            await analyzer_manager.update_progress(
                building_id, "COLMAP extraction failed."
            )
            return

    await deblur_gs_manager.start(building_id)
    center_session_id = "analyzer:center:" + building_id + uuid.uuid4().hex
    around_session_id = "analyzer:around:" + building_id + uuid.uuid4().hex
    await unity_manager.start(center_session_id)
    await unity_manager.start(around_session_id)

    async def update_deblur_gs_progress():
        try:
            while True:
                await analyzer_manager.update_progress(
                    building_id,
                    await deblur_gs_manager.get_progress(
                        deblur_gs_manager.building_to_client[building_id]
                    ),
                )
        except StopAsyncIteration:
            pass

    async def update_unity_ply():
        try:
            last_last_modified = get_last_modified(
                building_id + "/point_cloud.ply"
            )
            while True:
                last_modified = get_last_modified(
                    building_id + "/point_cloud.ply"
                )
                if last_modified != last_last_modified:
                    last_last_modified = last_modified
                    ply_url = get_presigned_upload_url(
                        building_id + "/point_cloud.ply",
                        "application/octet-stream",
                    )
                    await unity_manager.set_ply(
                        center_session_id,
                        ply_url,
                    )
                    await unity_manager.set_ply(
                        around_session_id,
                        ply_url,
                    )
                await asyncio.sleep(5)

        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Error sending PLY URL: {e}")

    update_deblur_gs_progress_task = asyncio.create_task(
        update_deblur_gs_progress()
    )
    update_unity_ply_task = asyncio.create_task(update_unity_ply())

    await update_deblur_gs_progress_task
    update_unity_ply_task.cancel()
    try:
        await update_unity_ply_task
    except asyncio.CancelledError:
        pass

    logger.info("Analyzer worker finished.")
