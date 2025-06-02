import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.logger import logger

from utils.authorization import is_valid_timestamp, verify_hmac
from dtos.base_dto import BaseWebSocketDTO
from managers import unity_manager


unity_router = APIRouter()


@unity_router.websocket("")
async def unity_route(websocket: WebSocket):
    client_id = "unity:" + websocket.client.host + ":" + uuid.uuid4().hex
    await unity_manager.accept(client_id, websocket)

    try:
        while True:
            dto = BaseWebSocketDTO(**json.loads(await websocket.receive_text()))
            logger.info(f"Received {client_id}\n{dto}")

    except Exception:
        await unity_manager.disconnect(client_id)
