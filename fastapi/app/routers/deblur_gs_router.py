import json
import uuid
from fastapi import APIRouter, WebSocket
from fastapi.logger import logger

from utils.authorization import is_valid_timestamp, verify_hmac
from dtos.base_dto import BaseWebSocketDTO
from dtos.deblur_gs_dto import UpdateDeblurGSProgressDTO
from managers import deblur_gs_manager
from services.deblur_gs_service import (
    complete_service,
    ply_url_service,
    stop_complete_service,
    update_progress_service,
    upload_complete_service,
)

deblur_gs_router = APIRouter()


@deblur_gs_router.websocket("")
async def deblur_gs_route(websocket: WebSocket):
    ts = websocket.query_params.get("ts")
    sig = websocket.query_params.get("sig")

    if not ts or not sig:
        await websocket.close(code=4001)
        return
    if not is_valid_timestamp(ts):
        await websocket.close(code=4002)
        return
    if not verify_hmac(ts, sig):
        await websocket.close(code=4003)
        return

    client_id = "deblur_gs-" + websocket.client.host + "-" + uuid.uuid4().hex
    await deblur_gs_manager.accept(client_id, websocket)

    try:
        while True:
            dto = BaseWebSocketDTO(**json.loads(await websocket.receive_text()))
            logger.info(f"Received {client_id}\n{dto}")
            if dto.type == "complete":
                await complete_service(client_id=client_id)
            if dto.type == "upload_complete":
                await upload_complete_service(client_id=client_id)
            if dto.type == "update_progress":
                await update_progress_service(
                    client_id=client_id,
                    dto=UpdateDeblurGSProgressDTO.model_validate(dto.data),
                )
            if dto.type == "ply_url":
                await ply_url_service(client_id=client_id)
            if dto.type == "stop_complete":
                await stop_complete_service(client_id=client_id)

    except Exception:
        await deblur_gs_manager.disconnect(client_id)
