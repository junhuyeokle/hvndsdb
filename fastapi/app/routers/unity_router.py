import json
import uuid

from fastapi import APIRouter, WebSocket
from fastapi.logger import logger

from dtos.base_dto import BaseSessionReadyDTO
from dtos.unity_dto import FrameDTO
from managers import unity_manager
from services.unity_service import (
    ready_service,
    frame_service,
)

unity_router = APIRouter()


@unity_router.websocket("")
async def unity_route(websocket: WebSocket):
    client_id = "unity-" + websocket.client.host + "-" + uuid.uuid4().hex
    await unity_manager.start_client(client_id, websocket)

    try:
        while True:
            message = json.loads(await websocket.receive_text())
            dto_type = message["type"]
            dto_data = message.get("data", {})

            if dto_type == BaseSessionReadyDTO.type:
                await ready_service(
                    client_id, BaseSessionReadyDTO.model_validate(dto_data)
                )
            elif dto_type == FrameDTO.type:
                await frame_service(
                    client_id, FrameDTO.model_validate(dto_data)
                )
            else:
                logger.warning(f"Unknown DTO type: {dto_type}")
    except Exception as e:
        logger.error(e)
        await unity_manager.end_client(client_id)
