import asyncio

from dtos.base_dto import BaseResponseDTO
from s3 import (
    download_file_from_presigned_url,
    download_folder_from_presigned_url,
    get_presigned_download_url,
    get_presigned_upload_url,
    is_key_exists,
    upload_folder_to_presigned_url,
)
from routers.deblur_gs_router import deblur_gs_manager
from services.workers import frames, colmap


async def start_analyzer_service(building_id: str):
    asyncio.create_task(analyze(building_id))

    return BaseResponseDTO(
        success=True,
        code=200,
        message="Analyze started successfully.",
        data=None,
    )


async def analyze(building_id: str):
    import logging
    import os

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    TEMP = "/temp"

    FRAMES = not is_key_exists(os.path.join(building_id, "frames.zip"))
    COLMAP = not is_key_exists(os.path.join(building_id, "colmap.zip"))
    DEBLUR_GS = not is_key_exists(os.path.join(building_id, "deblur_gs.zip"))

    logger.info(" ".join([str(b) for b in [FRAMES, COLMAP, DEBLUR_GS]]))

    sample_path = os.path.join(TEMP, building_id, "sample.mp4")
    colmap_path = os.path.join(TEMP, building_id, "colmap")
    frames_path = os.path.join(TEMP, building_id, "frames")

    logger.info(
        " ".join(
            [
                sample_path,
                colmap_path,
                frames_path,
                building_id,
            ]
        )
    )

    if FRAMES:
        logger.info("Downloading sample...")
        await download_file_from_presigned_url(
            get_presigned_download_url(os.path.join(building_id, "sample.mp4")),
            sample_path,
        )

        logger.info("Extracting frames...")
        if await frames.run(logger, sample_path, frames_path):
            logger.info("Uploading frames...")
            await upload_folder_to_presigned_url(
                get_presigned_upload_url(
                    os.path.join(building_id, "frames.zip"), "application/zip"
                ),
                frames_path,
                TEMP,
            )
        else:
            logger.error("Frame extraction failed.")
            return

    if COLMAP:
        if not FRAMES:
            logger.info("Downloading frames...")
            await download_folder_from_presigned_url(
                get_presigned_download_url(
                    os.path.join(building_id, "frames.zip")
                ),
                frames_path,
                TEMP,
            )

        logger.info("Extracting COLMAP data...")
        if await colmap.run(logger, colmap_path, frames_path):
            logger.info("Uploading COLMAP data...")
            await upload_folder_to_presigned_url(
                get_presigned_upload_url(
                    os.path.join(building_id, "colmap.zip"), "application/zip"
                ),
                colmap_path,
                TEMP,
            )
        else:
            logger.error("COLMAP extraction failed.")
            return

    if DEBLUR_GS:
        logger.info("Starting Deblur GS...")
        await deblur_gs_manager.start(building_id=building_id)

        while building_id in deblur_gs_manager.building_to_client:
            logger.info(await deblur_gs_manager.get_progress(building_id))

    logger.info("Analysis complete.")
