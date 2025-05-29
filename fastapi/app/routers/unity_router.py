import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from authorization import is_valid_timestamp, verify_hmac
from dtos.base_dto import BaseWebSocketDTO
from managers.unity_manager import UnityManager


unity_router = APIRouter()

manager = UnityManager()


@unity_router.websocket("/")
async def unity_route(ws: WebSocket):

    ts = ws.query_params.get("ts")
    sig = ws.query_params.get("sig")

    if not ts or not sig:
        await ws.close(code=4001)
        return
    if not is_valid_timestamp(ts):
        await ws.close(code=4002)
        return
    if not verify_hmac(ts, sig):
        await ws.close(code=4003)
        return

    client_id = ws.client.host
    manager.accept(client_id, ws)

    try:
        while True:
            raw = await ws.receive_text()
            dto = BaseWebSocketDTO(**json.loads(raw))

    except WebSocketDisconnect:
        manager.disconnect(client_id)
