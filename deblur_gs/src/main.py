import os
import shutil
import subprocess
import time
import websockets
import asyncio

from envs import SERVER_URL, TEMP, VISDOM_HOST, VISDOM_PORT, WS_KEY
from service import ply_url_service, start_service, stop_service, upload_service
from dto import BaseWebSocketDTO, PLYUrlDTO, StartDeblurGSDTO, UploadDeblurGSDTO
from utils import (
    generate_hmac_signature,
    get_last_point_cloud,
    upload_file_to_presigned_url,
)


async def watcher(
    base_path: str,
    sender_queue: asyncio.Queue,
    ply_url_condition: asyncio.Condition,
    shared_data: dict,
    interval: float = 5.0,
):
    while True:
        last_folder = get_last_point_cloud(base_path)

        if last_folder is not None:
            ply_file = os.path.join(last_folder, "point_cloud.ply")
            if os.path.exists(ply_file):
                await sender_queue.put(
                    BaseWebSocketDTO[None](type="ply_url", data=None).json()
                )
                print(f"Found PLY file: {ply_file}")

                async with ply_url_condition:
                    await ply_url_condition.wait()

                await upload_file_to_presigned_url(
                    shared_data["ply_url"], ply_file, "application/octet-stream"
                )

            shutil.rmtree(base_path)

        await asyncio.sleep(interval)


async def handler(
    dto: BaseWebSocketDTO,
    response_queue: asyncio.Queue,
    ply_url_condition: asyncio.Condition,
    shared_data: dict,
):
    print(f"Received\n{dto}")
    if dto.type == "start":
        await start_service(
            response_queue, StartDeblurGSDTO.parse_obj(dto.data), shared_data
        )

    elif dto.type == "stop":
        await stop_service(response_queue, shared_data)

    elif dto.type == "upload":
        await upload_service(
            response_queue, UploadDeblurGSDTO.parse_obj(dto.data)
        )

    elif dto.type == "ply_url":
        await ply_url_service(
            ply_url_condition,
            shared_data,
            PLYUrlDTO.parse_obj(dto.data),
        )

    else:
        print("Unknown message type:", dto.type)


async def sender(websocket, response_queue: asyncio.Queue):
    while True:
        message = await response_queue.get()
        print(f"Sending\n{message}")
        await websocket.send(message)


async def client():
    try:
        subprocess.Popen(
            [
                "python",
                "-m",
                "visdom.server",
                "-p",
                str(VISDOM_PORT),
                "--host",
                VISDOM_HOST,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"Visdom server started at http://{VISDOM_HOST}:{VISDOM_PORT}")
    except Exception as e:
        print(f"Failed to start Visdom server: {e}")
        return

    response_queue = asyncio.Queue()
    ply_url_condition = asyncio.Condition()
    shared_data = {}

    ts = str(int(time.time()))
    sig = generate_hmac_signature(ts, WS_KEY)
    url = f"{SERVER_URL}?ts={ts}&sig={sig}"

    async with websockets.connect(url) as websocket:
        print("Connected")

        sender_task = asyncio.create_task(sender(websocket, response_queue))
        watcher_task = asyncio.create_task(
            watcher(
                os.path.join(TEMP, "deblur_gs", "point_cloud"),
                response_queue,
                ply_url_condition,
                shared_data,
            )
        )

        async for request in websocket:
            await handler(
                BaseWebSocketDTO.parse_raw(request),
                response_queue,
                ply_url_condition,
                shared_data,
            )

    sender_task.cancel()
    try:
        await sender_task
    except asyncio.CancelledError:
        pass
    watcher_task.cancel()
    try:
        await watcher_task
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    try:
        asyncio.run(client())
    except asyncio.CancelledError:
        pass
