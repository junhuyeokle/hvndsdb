import json
import time
import hmac
import hashlib
import aiohttp
import websockets
import asyncio
import os
import zipfile
from pathlib import Path
from dotenv import load_dotenv
import subprocess

from utils import (
    download_folder_from_presigned_url,
    upload_folder_to_presigned_url,
)

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env")))

FASTAPI_HOST = os.getenv("FASTAPI_HOST")
FASTAPI_PORT = os.getenv("FASTAPI_PORT")
WS_KEY = os.getenv("WS_KEY")

ITERATION = 1
SAVE_ITERATION_INTERVAL = 500
SAVE_CHECKPOINT_INTERVAL = 1000

VISDOM_PORT = 8097
VISDOM_HOST = "127.0.0.1"

TEMP = os.path.abspath(os.path.join(os.path.dirname(__file__), "./temp"))
SERVER_URL = f"ws://{FASTAPI_HOST}:{FASTAPI_PORT}/ws/deblur_gs"


def generate_hmac_signature(ts: str, key: str) -> str:
    return hmac.new(key.encode(), ts.encode(), hashlib.sha256).hexdigest()


async def train(frames_url: str, colmap_url: str, send_queue: asyncio.Queue):
    await download_folder_from_presigned_url(
        frames_url, os.path.join(TEMP, "frames"), TEMP
    )
    await download_folder_from_presigned_url(
        colmap_url, os.path.join(TEMP, "colmap"), TEMP
    )

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

    cmd = [
        "python",
        "-u",
        "-m",
        "deblur_gs.train",
        "-s",
        os.path.join(TEMP, "colmap"),
        "-m",
        os.path.join(TEMP, "deblur_gs"),
        "-i",
        os.path.join(TEMP, "frames"),
        "--iterations",
        str(ITERATION),
        "--save_iterations",
        *[str(i) for i in range(0, ITERATION + 1, SAVE_ITERATION_INTERVAL)],
        "--checkpoint_iterations",
        *[str(i) for i in range(0, ITERATION + 1, SAVE_CHECKPOINT_INTERVAL)],
        "--test_iterations",
        "-1",
        "--deblur",
        "--visdom_server",
        VISDOM_HOST,
        "--visdom_port",
        str(VISDOM_PORT),
    ]

    print("Running command:", " ".join(cmd))

    loop = asyncio.get_running_loop()

    def launch_process():
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

    process = await loop.run_in_executor(None, launch_process)

    while process.poll() is None:
        line = await loop.run_in_executor(None, process.stdout.readline)
        if not line:
            continue
        line = line.strip()
        print(line)
        await send_queue.put(
            json.dumps(
                {
                    "type": "update_progress",
                    "data": {"progress": line},
                }
            )
        )

    await send_queue.put(json.dumps({"type": "complete", "data": None}))


async def handle_message(message: str, send_queue: asyncio.Queue):
    try:
        data = json.loads(message)
        msg_type = data.get("type")
        payload = data.get("data", {})

        if msg_type == "start":
            frames_url = payload.get("frames_url")
            colmap_url = payload.get("colmap_url")
            asyncio.create_task(train(frames_url, colmap_url, send_queue))

        elif msg_type == "upload":
            await upload_folder_to_presigned_url(
                payload.get("deblur_gs_url"),
                os.path.join(TEMP, "deblur_gs"),
                TEMP,
            )

            await send_queue.put(
                json.dumps({"type": "upload_complete", "data": None})
            )

        else:
            print("Unknown message type:", msg_type)
    except json.JSONDecodeError:
        print("Failed to parse message:", message)


async def websocket_sender(websocket, send_queue: asyncio.Queue):
    while True:
        message = await send_queue.get()
        await websocket.send(message)


async def connect():
    send_queue = asyncio.Queue()

    ts = str(int(time.time()))
    sig = generate_hmac_signature(ts, WS_KEY)
    url = f"{SERVER_URL}?ts={ts}&sig={sig}"

    try:
        async with websockets.connect(url) as websocket:
            print("Connected to server.")

            sender_task = asyncio.create_task(
                websocket_sender(websocket, send_queue)
            )

            async for message in websocket:
                await handle_message(message, send_queue)

            sender_task.cancel()
    except Exception as e:
        print("Connection failed:", e)


if __name__ == "__main__":
    asyncio.run(connect())
