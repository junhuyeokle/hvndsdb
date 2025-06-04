import json
import uuid

from fastapi import APIRouter, WebSocket
from fastapi.logger import logger
from starlette.requests import ClientDisconnect

from dtos.deblur_gs_dto import (
    ProgressDTO,
    UploadCompleteDTO,
    PLYUrlRequestDTO,
    CancelSessionCompleteDTO,
    CompleteDTO,
)
from managers import deblur_gs_manager
from services.deblur_gs_service import (
    complete_service,
    ply_url_request_service,
    cancel_complete_service,
    progress_service,
    upload_complete_service,
)
from utils.authorization import is_valid_timestamp, verify_hmac

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
    await deblur_gs_manager.start_client(client_id, websocket)

    try:
        while True:
            message = json.loads(await websocket.receive_text())
            dto_type = message["type"]
            dto_data = message.get("data", {})

            if dto_type == CompleteDTO.type:
                await complete_service(
                    client_id=client_id,
                    dto=CompleteDTO.model_validate(dto_data),
                )
            elif dto_type == UploadCompleteDTO.type:
                await upload_complete_service(
                    client_id=client_id,
                    dto=UploadCompleteDTO.model_validate(dto_data),
                )
            elif dto_type == ProgressDTO.type:
                await progress_service(
                    client_id=client_id,
                    dto=ProgressDTO.model_validate(dto_data),
                )
            elif dto_type == PLYUrlRequestDTO.type:
                await ply_url_request_service(
                    client_id=client_id,
                    dto=PLYUrlRequestDTO.model_validate(dto_data),
                )
            elif dto_type == CancelSessionCompleteDTO.type:
                await cancel_complete_service(
                    client_id=client_id,
                    dto=CancelSessionCompleteDTO.model_validate(dto_data),
                )
            else:
                logger.warning(f"Unknown DTO type {dto_type}")
    except ClientDisconnect:
        pass
    except Exception as e:
        logger.error(f"Unhandled Exception {e}")
    finally:
        await deblur_gs_manager.end_client(client_id)
