import asyncio
import math
import os
import shutil
import uuid

from fastapi.logger import logger
from pyglm import glm

from dtos.base_dto import BaseEndSessionDTO
from managers import deblur_gs_manager, unity_manager, analyzer_manager
from tasks import frames_task, colmap_task
from utils.envs import TEMP
from utils.s3 import (
    download_file_from_presigned_url,
    download_folder_from_presigned_url,
    get_last_modified,
    get_presigned_download_url,
    get_presigned_upload_url,
    is_key_exists,
    upload_folder_to_presigned_url,
)


async def run(building_id: str):
    FRAMES = not is_key_exists(os.path.join(building_id, "frames.zip"))
    COLMAP = not is_key_exists(os.path.join(building_id, "colmap.zip"))

    if os.path.isdir(os.path.join(TEMP, building_id)):
        shutil.rmtree(os.path.join(TEMP, building_id))

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

        if not await frames_task.run(sample_path, frames_path, building_id):
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

        if not await colmap_task.run(colmap_path, frames_path, building_id):
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
    try:
        deblur_gs_client_id = await deblur_gs_manager.start_session(building_id)
        logger.info(deblur_gs_client_id)
        deblur_gs_session = deblur_gs_manager.get_client(
            deblur_gs_client_id
        ).get_session(building_id)
        logger.info(deblur_gs_session)
        center_session_id = (
                "unity-center-" + building_id + "-" + uuid.uuid4().hex
        )
        around_session_id = (
                "unity-around-" + building_id + "-" + uuid.uuid4().hex
        )
        center_client_id = await unity_manager.start_session(center_session_id)
        around_client_id = await unity_manager.start_session(around_session_id)
        center_session = unity_manager.get_client(center_client_id).get_session(
            center_session_id
        )
        around_session = unity_manager.get_client(around_client_id).get_session(
            around_session_id
        )
    except Exception as e:
        logger.error(f"Error starting sessions: {e}")

    async def update_deblur_gs_progress():
        try:
            while True:
                await analyzer_manager.update_progress(
                    building_id, await deblur_gs_session.get_progress()
                )
        except StopAsyncIteration:
            pass

    async def update_center_frame():
        try:
            while True:
                await analyzer_manager.update_center_frame(
                    building_id,
                    await center_session.get_frame(),
                )
        except StopAsyncIteration:
            pass
        except asyncio.CancelledError:
            raise

    async def update_around_frame():
        try:
            while True:
                await analyzer_manager.update_around_frame(
                    building_id,
                    await around_session.get_frame(),
                )
        except StopAsyncIteration:
            pass
        except asyncio.CancelledError:
            raise

    FPS = 10
    ROTATION_SPEED = 60

    async def update_center_transform():
        await center_session.wait_ready()
        try:
            angle_deg = 0.0

            while True:
                angle_rad = math.radians(angle_deg)
                quat = glm.angleAxis(angle_rad, glm.vec3(0, 1, 0))

                await center_session.set_camera_rotation(
                    quat.x, quat.y, quat.z, quat.w
                )

                angle_deg = (angle_deg + ROTATION_SPEED / FPS) % 360
                await asyncio.sleep(1 / FPS)

        except asyncio.CancelledError:
            raise

    async def update_around_transform():
        await around_session.wait_ready()
        try:
            angle_deg = 0.0
            radius = 30
            height = 10

            while True:
                angle_rad = math.radians(angle_deg)

                x = radius * math.cos(angle_rad)
                z = radius * math.sin(angle_rad)
                y = height
                position = glm.vec3(x, y, z)

                forward = glm.normalize(position - glm.vec3(0.0))
                up = glm.vec3(0, 1, 0)
                quat = glm.quatLookAt(forward, up)

                await around_session.set_camera_position(x, y, z)

                await around_session.set_camera_rotation(
                    quat.x, quat.y, quat.z, quat.w
                )

                angle_deg = (angle_deg + ROTATION_SPEED / FPS) % 360
                await asyncio.sleep(1 / FPS)

        except asyncio.CancelledError:
            raise

    async def update_unity_ply():
        await center_session.wait_ready()
        await around_session.wait_ready()
        try:
            last_last_modified = None
            while True:
                last_modified = get_last_modified(
                    building_id + "/point_cloud.ply"
                )
                if last_modified != last_last_modified:
                    last_last_modified = last_modified
                    ply_url = get_presigned_download_url(
                        building_id + "/point_cloud.ply"
                    )
                    await center_session.set_ply(ply_url)
                    await around_session.set_ply(ply_url)
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            raise

    update_deblur_gs_progress_task = asyncio.create_task(
        update_deblur_gs_progress()
    )
    update_center_frame_task = asyncio.create_task(update_center_frame())
    update_around_frame_task = asyncio.create_task(update_around_frame())
    update_center_transform_task = asyncio.create_task(
        update_center_transform()
    )
    update_around_transform_task = asyncio.create_task(
        update_around_transform()
    )
    update_unity_ply_task = asyncio.create_task(update_unity_ply())

    await update_deblur_gs_progress_task

    update_center_frame_task.cancel()
    try:
        await update_center_frame_task
    except asyncio.CancelledError:
        pass

    update_around_frame_task.cancel()
    try:
        await update_around_frame_task
    except asyncio.CancelledError:
        pass

    update_center_transform_task.cancel()
    try:
        await update_center_transform_task
    except asyncio.CancelledError:
        pass

    update_around_transform_task.cancel()
    try:
        await update_around_transform_task
    except asyncio.CancelledError:
        pass

    update_unity_ply_task.cancel()
    try:
        await update_unity_ply_task
    except asyncio.CancelledError:
        pass

    await unity_manager.get_client(center_client_id).end_session(
        center_session_id, BaseEndSessionDTO(session_id=center_session_id)
    )
    await unity_manager.get_client(around_client_id).end_session(
        around_session_id, BaseEndSessionDTO(session_id=around_session_id)
    )

    logger.info("Analyzer worker finished.")
