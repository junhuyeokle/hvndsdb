from typing import Dict

from fastapi import WebSocket

from dtos.base_dto import BaseWebSocketDTO


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    def connect(self, client_id: str, websocket: WebSocket):
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)

    def get(self, client_id: str) -> WebSocket | None:
        return self.active_connections.get(client_id)

    async def send(self, client_id: str, dto: BaseWebSocketDTO):
        ws = self.get(client_id)
        if ws:
            await ws.send_json(dto.model_dump(mode="json"))
