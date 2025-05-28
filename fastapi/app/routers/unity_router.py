import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from dtos.base_dto import BaseWebSocketDTO
from web_socket import WebSocketManager


class UnityManager(WebSocketManager):
    def __init__(self):
        super().__init__()
        self.processing_buildings = set()


unity_router = APIRouter()

manager = UnityManager()


@unity_router.websocket("/")
async def unity_route(ws: WebSocket):
    client_id = ws.client.host
    manager.connect(client_id, ws)

    try:
        while True:
            raw = await ws.receive_text()
            dto = BaseWebSocketDTO(**json.loads(raw))

    except WebSocketDisconnect:
        manager.disconnect(client_id)
