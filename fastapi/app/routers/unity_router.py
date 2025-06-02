import json
import uuid
from fastapi import APIRouter, WebSocket
from fastapi.logger import logger

from dtos.unity_dto import FrameDTO, StartSessionCompleteDTO
from services.unity_service import (
    start_session_complete_service,
    update_frame_service,
)
from dtos.base_dto import BaseWebSocketDTO
from managers import unity_manager


unity_router = APIRouter()


@unity_router.websocket("")
async def unity_route(websocket: WebSocket):
    client_id = "unity-" + websocket.client.host + "-" + uuid.uuid4().hex
    await unity_manager.accept(client_id, websocket)

    try:
        while True:
            dto = BaseWebSocketDTO(**json.loads(await websocket.receive_text()))
            logger.info(f"Received {client_id}\n{dto}")
            if dto.type == "start_session_complete":
                start_session_complete_service(
                    StartSessionCompleteDTO.model_validate(dto.data)
                )
            if dto.type == "frame":
                await update_frame_service(FrameDTO.model_validate(dto.data))
    except Exception:
        await unity_manager.disconnect(client_id)
