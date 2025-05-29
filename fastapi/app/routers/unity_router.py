import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from authorization import is_valid_timestamp, verify_hmac
from dtos.base_dto import BaseWebSocketDTO
from managers.unity_manager import UnityManager


unity_router = APIRouter()

unity_manager = UnityManager()


@unity_router.websocket("/")
async def unity_route(websocket: WebSocket):

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

    client_id = websocket.client.host
    await unity_manager.accept(client_id, websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            dto = BaseWebSocketDTO(**json.loads(raw))

    except WebSocketDisconnect:
        await unity_manager.disconnect(client_id)
