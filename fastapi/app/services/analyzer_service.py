import asyncio

from dtos.base_dto import BaseResponseDTO
from sc3 import (
    download_file_from_presigned_url,
    get_presigned_download_url,
    get_presigned_upload_url,
    upload_folder_to_presigned_url,
)
from routers.deblur_gs_router import deblur_gs_manager

TEMP = "./temp"


async def start_analyzer_service(building_id: str):
    asyncio.create_task(analyze(building_id))

    return BaseResponseDTO(
        success=True,
        code=200,
        message="Analyze started successfully.",
        data=None,
    )


async def run_worker_async(
    logger,
    task: str,
    colmap_path: str,
    frames_path: str = None,
):
    args = ["python", "./services/analyzer_worker.py", task, colmap_path]
    if frames_path:
        args.append(frames_path)

    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        logger.info(f"[ERROR] {task} failed:\n{stderr.decode().strip()}")
    else:
        logger.info(f"[SUCCESS] {task} complete:\n{stdout.decode().strip()}")


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

    class Config:
        DATA_PATH = TEMP

        def __init__(
            self,
            building_id,
            EXTRACT_FRAMES=True,
            EXTRACT_FEATURES=True,
            MATCH_HYBRID=False,
            MATCH_SEQUENTIAL=True,
            MATCH_EXHAUSTIVE=False,
            INCREMENTAL_MAPPING=True,
            TRAIN=True,
        ):
            self.sample_path = os.path.join(
                Config.DATA_PATH, building_id, "sample.mp4"
            )
            self.deblur_gs_path = os.path.join(
                Config.DATA_PATH, building_id, "deblur_gs"
            )
            self.colmap_path = os.path.join(
                Config.DATA_PATH, building_id, "colmap"
            )
            self.frames_path = os.path.join(
                Config.DATA_PATH, building_id, "frames"
            )

            self.EXTRACT_FRAMES = EXTRACT_FRAMES
            self.EXTRACT_FEATURES = EXTRACT_FEATURES
            self.MATCH_HYBRID = MATCH_HYBRID
            self.MATCH_SEQUENTIAL = MATCH_SEQUENTIAL
            self.MATCH_EXHAUSTIVE = MATCH_EXHAUSTIVE
            self.INCREMENTAL_MAPPING = INCREMENTAL_MAPPING
            self.TRAIN = TRAIN

            self.MATCH_SEQUENTIAL = (
                False if self.MATCH_HYBRID else self.MATCH_SEQUENTIAL
            )
            self.MATCH_EXHAUSTIVE = (
                False if self.MATCH_HYBRID else self.MATCH_EXHAUSTIVE
            )

    config = Config(building_id=building_id)

    logger.info(
        " ".join(
            [
                config.sample_path,
                config.colmap_path,
                config.frames_path,
                building_id,
            ]
        )
    )

    await download_file_from_presigned_url(
        get_presigned_download_url(building_id + "/sample.mp4"),
        config.sample_path,
    )

    if config.EXTRACT_FRAMES:
        logger.info("Extracting frames...")
        await run_worker_async(
            logger, "extract_frames", config.sample_path, config.frames_path
        )

        await upload_folder_to_presigned_url(
            get_presigned_upload_url(
                building_id + "/frames.zip", "application/zip"
            ),
            config.frames_path,
        )

    if config.EXTRACT_FEATURES:
        logger.info("Extracting features...")
        await run_worker_async(
            logger, "extract_features", config.colmap_path, config.frames_path
        )

    if config.MATCH_SEQUENTIAL:
        logger.info("Matching sequentially...")
        await run_worker_async(logger, "match_sequential", config.colmap_path)

    if config.MATCH_EXHAUSTIVE:
        logger.info("Matching exhaustively...")
        await run_worker_async(logger, "match_exhaustive", config.colmap_path)

    if config.MATCH_HYBRID:
        logger.info("Matching hybrid...")
        await run_worker_async(logger, "match_hybrid", config.colmap_path)

    if config.INCREMENTAL_MAPPING:
        logger.info("Running incremental mapping...")
        await run_worker_async(
            logger,
            "incremental_mapping",
            config.colmap_path,
            config.frames_path,
        )

    logger.info("Uploading COLMAP data...")
    await upload_folder_to_presigned_url(
        get_presigned_upload_url(
            building_id + "/colmap.zip", "application/zip"
        ),
        config.colmap_path,
    )

    await deblur_gs_manager.start_deblur_gs(building_id=building_id)
