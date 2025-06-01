import os

from fastapi.logger import logger
from utils.envs import TEMP
from managers import deblur_gs_manager
from managers import analyzer_manager
from utils.s3 import (
    download_file_from_presigned_url,
    download_folder_from_presigned_url,
    get_presigned_download_url,
    get_presigned_upload_url,
    is_key_exists,
    upload_folder_to_presigned_url,
)
from workers import colmap_worker, frames_worker


async def run(client_id: str):
    building_id = analyzer_manager.get_shared_data(client_id).get("building_id")

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
            get_presigned_download_url(os.path.join(building_id, "sample.mp4")),
            sample_path,
        )

        if not await frames_worker.run(sample_path, frames_path, client_id):
            await upload_folder_to_presigned_url(
                get_presigned_upload_url(
                    os.path.join(building_id, "frames.zip"),
                    "application/zip",
                ),
                frames_path,
            )
        else:
            await analyzer_manager.update_progress(
                client_id, "Frames extraction failed."
            )
            return

    if COLMAP:
        if not FRAMES:
            await download_folder_from_presigned_url(
                get_presigned_download_url(
                    os.path.join(building_id, "frames.zip")
                ),
                frames_path,
            )

        if not await colmap_worker.run(colmap_path, frames_path, client_id):
            await upload_folder_to_presigned_url(
                get_presigned_upload_url(
                    os.path.join(building_id, "colmap.zip"),
                    "application/zip",
                ),
                colmap_path,
            )
        else:
            await analyzer_manager.update_progress(
                client_id, "COLMAP extraction failed."
            )
            return

    await deblur_gs_manager.start(building_id)

    try:
        while True:
            await analyzer_manager.update_progress(
                client_id,
                await deblur_gs_manager.get_progress(
                    deblur_gs_manager.building_to_client[building_id]
                ),
            )
    except StopAsyncIteration:
        pass

    logger.info("Analyzer worker finished.")
