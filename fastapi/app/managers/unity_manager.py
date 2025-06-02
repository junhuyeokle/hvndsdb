from typing import Optional
from dtos.base_dto import BaseWebSocketDTO
from dtos.unity_dto import SetPlyDTO, StartSessionDTO
from managers.web_socket_manager import WebSocketManager


class UnityManager(WebSocketManager):
    def __init__(self):
        super().__init__()
        self.session_to_client: dict[str, str] = {}

    async def start(self, session_id: str, client_id: Optional[str] = None):
        if not client_id:
            if not self.connections:
                raise RuntimeError("No client connected to start Unity.")
            client_id = next(iter(self.connections))

        self.get_shared_data(client_id).setdefault("session_id", set()).add(
            session_id
        )

        self.session_to_client[session_id] = client_id

        await self.send(
            client_id,
            BaseWebSocketDTO[StartSessionDTO](
                type="start_session",
                data=StartSessionDTO(session_id=session_id),
            ),
        )

    async def set_ply(self, session_id: str, ply_url: str):
        client_id = self.session_to_client.get(session_id)
        if not client_id:
            raise LookupError(
                f"No client associated with session {session_id}."
            )

        await self.send(
            client_id,
            BaseWebSocketDTO[SetPlyDTO](
                type="set_ply",
                data=SetPlyDTO(ply_url=ply_url, session_id=session_id),
            ),
        )
