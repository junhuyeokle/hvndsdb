import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from authorization import is_valid_timestamp, verify_hmac
from dtos.base_dto import BaseWebSocketDTO
from managers.deblur_gs_manager import DeblurGSManager
from services.deblur_gs_service import (
    complete_service,
    upload_complete_service,
)

deblur_gs_router = APIRouter()

manager = DeblurGSManager()


@deblur_gs_router.websocket("")
async def deblur_gs_route(websocket: WebSocket):
    ts = websocket.query_params.get("ts")
    sig = websocket.query_params.get("sig")

    print(f"ts: {ts}, sig: {sig}")
    if not ts or not sig:
        await websocket.close(code=4001)
        return
    if not is_valid_timestamp(ts):
        print("Invalid timestamp")
        await websocket.close(code=4002)
        return
    if not verify_hmac(ts, sig):
        print("HMAC verification failed")
        await websocket.close(code=4003)
        return

    client_id = websocket.client.host
    await manager.accept(client_id, websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            dto = BaseWebSocketDTO(**json.loads(raw))
            if dto.type == "complete":
                await complete_service(client_id=client_id, manager=manager)
            if dto.type == "upload_complete":
                upload_complete_service(client_id=client_id, manager=manager)

    except WebSocketDisconnect:
        await manager.disconnect(client_id)
