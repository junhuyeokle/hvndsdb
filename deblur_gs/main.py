import json
import time
import hmac
import hashlib
import websockets
import aiohttp
import asyncio
import os
import zipfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

print(os.path.join(os.path.dirname(__file__), "../.env"))

FASTAPI_HOST = os.getenv("FASTAPI_HOST")
FASTAPI_PORT = os.getenv("FASTAPI_PORT")
WS_KEY = os.getenv("WS_KEY")

print(
    f"FASTAPI_HOST: {FASTAPI_HOST}, FASTAPI_PORT: {FASTAPI_PORT}, WS_KEY: {WS_KEY}"
)

TEMP = "./temp"

SERVER_URL = f"ws://{FASTAPI_HOST}:{FASTAPI_PORT}/ws/deblur_gs"


def generate_hmac_signature(ts: str, key: str) -> str:
    return hmac.new(key.encode(), ts.encode(), hashlib.sha256).hexdigest()


async def download_folder_from_presigned_url(url: str, path: str):
    target_dir = Path(TEMP)
    target_dir.mkdir(parents=True, exist_ok=True)
    zip_path = target_dir / f"{path}.zip"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Download failed: {response.status}")
                return
            with open(zip_path, "wb") as f:
                f.write(await response.read())
            print(f"Downloaded to: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        extract_path = target_dir / path
        zip_ref.extractall(extract_path)
        print(f"Extracted to: {extract_path}")


async def handle_message(websocket, message):
    try:
        data = json.loads(message)
        msg_type = data.get("type")
        payload = data.get("data", {})

        if msg_type == "start":
            print("start received")
            frames_url = payload.get("frames_url")
            colmap_url = payload.get("colmap_url")
            print("frames_url:", frames_url)
            print("colmap_url:", colmap_url)

            await download_folder_from_presigned_url(frames_url, "frames")
            await download_folder_from_presigned_url(colmap_url, "colmap")

            await websocket.send(json.dumps({"type": "complete", "data": None}))

        elif msg_type == "upload":
            print("upload received")
            print("deblur_gs_url:", payload.get("deblur_gs_url"))

            await websocket.send(
                json.dumps({"type": "upload_complete", "data": None})
            )

        else:
            print("Unknown message type:", msg_type)

    except json.JSONDecodeError:
        print("Failed to parse message:", message)


async def connect():
    ts = str(int(time.time()))
    sig = generate_hmac_signature(ts, WS_KEY)
    url = f"{SERVER_URL}?ts={ts}&sig={sig}"

    try:
        async with websockets.connect(url) as websocket:
            print("Connected to server.")
            async for message in websocket:
                await handle_message(websocket, message)
    except Exception as e:
        print("Connection failed:", e)


if __name__ == "__main__":
    asyncio.run(connect())
