import asyncio
import os
from envs import TEMP
import train_worker
from dto import PLYUrlDTO, StartDeblurGSDTO, BaseWebSocketDTO, UploadDeblurGSDTO
from utils import (
    clean_deblur_gs,
    download_folder_from_presigned_url,
    upload_folder_to_presigned_url,
)


async def start_service(response_queue: asyncio.Queue, dto: StartDeblurGSDTO, shared_data: dict):
    await download_folder_from_presigned_url(
        dto.frames_url, os.path.join(TEMP, "frames")
    )

    await download_folder_from_presigned_url(
        dto.colmap_url, os.path.join(TEMP, "colmap")
    )

    train_task = asyncio.create_task(
        train_worker.run(
            response_queue,
            os.path.join(TEMP, "colmap"),
            os.path.join(TEMP, "frames"),
            os.path.join(TEMP, "deblur_gs"),
        )
    )

    shared_data["train_task"] = train_task


async def stop_service(response_queue: asyncio.Queue, shared_data: dict):
    train_task = shared_data.get("train_task")
    if train_task:
        train_task.cancel()
        try:
            await train_task
        except asyncio.CancelledError:
            pass

    await response_queue.put(
        BaseWebSocketDTO[None](type="stop_complete", data=None).json()
    )


async def upload_service(response_queue: asyncio.Queue, dto: UploadDeblurGSDTO):
    clean_deblur_gs(os.path.join(TEMP, "deblur_gs"))

    await upload_folder_to_presigned_url(
        dto.deblur_gs_url,
        os.path.join(TEMP, "deblur_gs"),
    )

    await response_queue.put(
        BaseWebSocketDTO[None](type="upload_complete", data=None).json()
    )


async def ply_url_service(
    ply_url_condition: asyncio.Condition, shared_data: dict, dto: PLYUrlDTO
):
    async with ply_url_condition:
        ply_url_condition.notify()
        shared_data["ply_url"] = dto.ply_url
