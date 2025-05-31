import os
import shutil
import subprocess
import time
import websockets
import asyncio

from envs import SERVER_URL, VISDOM_HOST, VISDOM_PORT, WS_KEY
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
    base_path = os.path.abspath(base_path)

    while True:
        last_folder = get_last_point_cloud(base_path)

        if last_folder is not None:
            ply_file = os.path.join(last_folder, "point_cloud.ply")
            if os.path.exists(ply_file):
                await sender_queue.put(
                    BaseWebSocketDTO[None](
                        type="update_progress",
                        data={"progress": "Uploading point cloud..."},
                    ).json()
                )

                async with ply_url_condition:
                    await ply_url_condition.wait()

                await upload_file_to_presigned_url(
                    shared_data["ply_url"], ply_file, "application/octet-stream"
                )

            for name in os.listdir(base_path):
                full_path = os.path.join(base_path, name)
                if os.path.isdir(full_path) and full_path != last_folder:
                    shutil.rmtree(full_path)
                    print(f"Deleted: {full_path}")
        else:
            print("No valid folders found.")

        await asyncio.sleep(interval)


async def handler(
    dto: BaseWebSocketDTO,
    response_queue: asyncio.Queue,
    ply_url_condition: asyncio.Condition,
    shared_data: dict,
):
    if dto.type == "start":
        await start_service(
            response_queue, StartDeblurGSDTO.parse_obj(dto.data), shared_data
        )

    elif dto.type == "stop":
        await stop_service(
            response_queue, UploadDeblurGSDTO.parse_obj(dto.data), shared_data
        )

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

    try:
        async with websockets.connect(url) as websocket:
            print("Connected to server.")

            sender_task = asyncio.create_task(sender(websocket, response_queue))
            watcher_task = asyncio.create_task(
                watcher(
                    os.path.join("temp", "deblur_gs"),
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
            watcher_task.cancel()
    except Exception as e:
        print("Connection failed:", e)


if __name__ == "__main__":
    asyncio.run(client())
