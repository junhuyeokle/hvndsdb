import json
import uuid

from fastapi import APIRouter, WebSocket
from fastapi.logger import logger

from dtos.analyzer_dto import CancelDeblurGS
from dtos.base_dto import BaseStartSessionDTO
from managers import analyzer_manager
from services.analyzer_service import (
    start_session_service,
    cancel_deblur_gs_service,
)

analyzer_router = APIRouter()


@analyzer_router.websocket("")
async def analyzer_route(websocket: WebSocket):
    client_id = "analyzer-" + websocket.client.host + "-" + uuid.uuid4().hex
    await analyzer_manager.start_client(client_id, websocket)

    try:
        while True:
            message = json.loads(await websocket.receive_text())
            dto_type = message["type"]
            dto_data = message.get("data", {})

            if dto_type == BaseStartSessionDTO.type:
                start_session_service(
                    BaseStartSessionDTO.model_validate(dto_data)
                )
            elif dto_type == CancelDeblurGS.type:
                await cancel_deblur_gs_service(
                    CancelDeblurGS.model_validate(dto_data)
                )
            else:
                logger.error(f"Unknown DTO type: {dto_type}")
    except Exception as e:
        logger.error(e)
        await analyzer_manager.end_client(client_id)
