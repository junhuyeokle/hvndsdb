from typing import Dict

from fastapi import WebSocket
from fastapi.logger import logger

from dtos.base_dto import BaseWebSocketDTO


class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, tuple[WebSocket, dict]] = {}

    async def accept(self, client_id: str, websocket: WebSocket):
        logger.info(f"Accepting {client_id}")
        await websocket.accept()
        self.connections[client_id] = (websocket, {})

    async def disconnect(self, client_id: str):
        logger.info(f"Disconnecting {client_id}")
        connection = self.connections.get(client_id)
        if connection:
            websocket, _ = connection
            try:
                await websocket.close()
            except Exception:
                pass
            self.connections.pop(client_id, None)

    def get_web_socket(self, client_id: str) -> WebSocket | None:
        connection = self.connections.get(client_id)
        return connection[0] if connection else None

    def get_shared_data(self, client_id: str) -> dict | None:
        connection = self.connections.get(client_id)
        return connection[1] if connection else None

    def set_shared_data(self, client_id: str, key: str, value):
        if client_id in self.connections:
            _, shared_data = self.connections[client_id]
            shared_data[key] = value

    async def send(self, client_id: str, dto: BaseWebSocketDTO):
        logger.info(f"Sending {client_id}\n{dto}")
        websocket = self.get_web_socket(client_id)
        if websocket:
            await websocket.send_json(dto.model_dump(mode="json"))
