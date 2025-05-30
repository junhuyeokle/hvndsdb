import time
import websockets
import asyncio

from envs import SERVER_URL, WS_KEY
from service import start_service, upload_service
from dto import BaseWebSocketDTO, StartDeblurGSDTO, UploadDeblurGSDTO
from utils import (
    generate_hmac_signature,
)


async def handler(dto: BaseWebSocketDTO, response_queue: asyncio.Queue):
    if dto.type == "start":
        await start_service(
            response_queue, StartDeblurGSDTO.parse_obj(dto.data)
        )

    elif dto.type == "upload":
        await upload_service(
            response_queue, UploadDeblurGSDTO.parse_obj(dto.data)
        )

    else:
        print("Unknown message type:", dto.type)


async def sender(websocket, response_queue: asyncio.Queue):
    while True:
        message = await response_queue.get()
        await websocket.send(message)


async def client():
    response_queue = asyncio.Queue()

    ts = str(int(time.time()))
    sig = generate_hmac_signature(ts, WS_KEY)
    url = f"{SERVER_URL}?ts={ts}&sig={sig}"

    try:
        async with websockets.connect(url) as websocket:
            print("Connected to server.")

            sender_task = asyncio.create_task(sender(websocket, response_queue))

            async for request in websocket:
                await handler(
                    BaseWebSocketDTO.parse_raw(request), response_queue
                )

            sender_task.cancel()
    except Exception as e:
        print("Connection failed:", e)


if __name__ == "__main__":
    asyncio.run(client())
