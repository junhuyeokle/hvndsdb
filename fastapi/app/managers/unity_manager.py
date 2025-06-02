import asyncio
from typing import Optional, Set
from dtos.base_dto import BaseWebSocketDTO
from dtos.unity_dto import (
    SetCameraPositionDTO,
    SetCameraRotationDTO,
    SetPlyDTO,
    StartSessionDTO,
    StopSessionDTO,
)
from managers.web_socket_manager import WebSocketManager


class UnityManager(WebSocketManager):
    def __init__(self):
        super().__init__()
        self.session_to_client: dict[str, str] = {}
        self.start_session_completes: dict[str, asyncio.Event] = {}
        self.frames: dict[str, asyncio.Queue] = {}

    async def start_session(
        self, session_id: str, client_id: Optional[str] = None
    ):
        if not client_id:
            if not self.connections:
                raise RuntimeError("No client connected to start Unity.")
            client_id = next(iter(self.connections))

        session_ids: Set[str] = self.get_shared_data(client_id).setdefault(
            "session_ids", set()
        )
        session_ids.add(session_id)

        self.session_to_client[session_id] = client_id
        self.start_session_completes[session_id] = asyncio.Event()
        self.frames[session_id] = asyncio.Queue()

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

    async def set_camera_position(
        self, session_id: str, x: float, y: float, z: float
    ):
        client_id = self.session_to_client.get(session_id)
        if not client_id:
            raise LookupError(
                f"No client associated with session {session_id}."
            )

        await self.send(
            client_id,
            BaseWebSocketDTO[SetCameraPositionDTO](
                type="set_camera_position",
                data=SetCameraPositionDTO(session_id=session_id, x=x, y=y, z=z),
            ),
        )

    async def set_camera_rotation(
        self, session_id: str, x: float, y: float, z: float, w: float
    ):
        client_id = self.session_to_client.get(session_id)
        if not client_id:
            raise LookupError(
                f"No client associated with session {session_id}."
            )

        await self.send(
            client_id,
            BaseWebSocketDTO[SetCameraRotationDTO](
                type="set_camera_rotation",
                data=SetCameraRotationDTO(
                    session_id=session_id, x=x, y=y, z=z, w=w
                ),
            ),
        )

    async def update_frame(self, session_id: str, frame: str):
        await self.frames[session_id].put(frame)

    async def get_frame(self, session_id: str):
        frame = await self.frames[session_id].get()

        if frame is None:
            raise StopAsyncIteration

        return frame

    async def stop_session(self, session_id: str):
        client_id = self.session_to_client.pop(session_id, None)
        if not client_id:
            raise LookupError(
                f"No client associated with session {session_id}."
            )

        await self.send(
            client_id,
            BaseWebSocketDTO[StopSessionDTO](
                type="stop_session",
                data=StopSessionDTO(session_id=session_id),
            ),
        )

        self.start_session_completes.pop(session_id).set()
        await self.frames.pop(session_id).put(None)

        session_ids: Set[str] = self.get_shared_data(client_id)["session_ids"]
        session_ids.discard(session_id)

    async def disconnect(self, client_id):
        session_ids: Set[str] = self.get_shared_data(client_id)["session_ids"]
        for session_id in list(session_ids):
            await self.stop_session(session_id)
        await super().disconnect(client_id)
