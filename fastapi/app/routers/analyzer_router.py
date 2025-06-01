import json
from fastapi import APIRouter, WebSocket

from dtos.analyzer_dto import StartAnalyzerDTO
from dtos.base_dto import BaseWebSocketDTO
from managers.analyzer_manager import analyzer_manager
from services.analyzer_service import start_service, stop_deblur_gs_service
from fastapi.logger import logger

analyzer_router = APIRouter()


@analyzer_router.websocket("")
async def analyzer_route(websocket: WebSocket):
    client_id = websocket.client.host
    await analyzer_manager.accept(client_id, websocket)

    try:
        while True:
            dto = BaseWebSocketDTO(**json.loads(await websocket.receive_text()))
            logger.info(f"Received\n{dto}")
            if dto.type == "start":
                await start_service(
                    client_id, StartAnalyzerDTO.model_validate(dto.data)
                )
            if dto.type == "stop_deblur_gs":
                await stop_deblur_gs_service(client_id=client_id)

    except Exception:
        await analyzer_manager.disconnect(client_id)
