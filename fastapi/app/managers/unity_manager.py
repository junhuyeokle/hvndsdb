import asyncio

from dtos.base_dto import (
    BaseWebSocketDTO,
    BaseEndSessionDTO,
    BaseStartSessionDTO,
)
from dtos.unity_dto import (
    CancelSessionDTO,
    SetCameraPositionDTO,
    SetCameraRotationDTO,
    SetPlyDTO,
)
from managers.web_socket_manager import (
    WebSocketManager,
    WebsocketSession,
    WebsocketClient,
)


class UnityClient(WebsocketClient):
    async def cancel_session(self, session_id: str):
        await self.send(
            BaseWebSocketDTO[CancelSessionDTO](
                data=CancelSessionDTO(session_id=session_id),
            ),
        )

        session: UnitySession = self.get_session(session_id)
        await session.put_frame(None)

    async def end_session(
        self, session_id: str, dto: BaseWebSocketDTO[BaseEndSessionDTO]
    ):
        session: UnitySession = self.get_session(session_id)
        await session.put_frame(None)
        await super().end_session(session_id, dto)


class UnitySession(WebsocketSession):
    def __init__(self, session_id: str, client: UnityClient):
        super().__init__(session_id, client)
        self._frames: asyncio.Queue = asyncio.Queue()

    async def set_ply(self, ply_url: str):
        await self._client.send(
            BaseWebSocketDTO[SetPlyDTO](
                data=SetPlyDTO(ply_url=ply_url, session_id=self._session_id),
            ),
        )

    async def set_camera_position(self, x: float, y: float, z: float):
        await self._client.send(
            BaseWebSocketDTO[SetCameraPositionDTO](
                data=SetCameraPositionDTO(
                    session_id=self._session_id, x=x, y=y, z=z
                ),
            ),
        )

    async def set_camera_rotation(self, x: float, y: float, z: float, w: float):
        await self._client.send(
            BaseWebSocketDTO[SetCameraRotationDTO](
                data=SetCameraRotationDTO(
                    session_id=self._session_id, x=x, y=y, z=z, w=w
                ),
            ),
        )

    async def put_frame(self, frame: str | None):
        await self._frames.put(frame)

    async def get_frame(self):
        frame = await self._frames.get()

        if frame is None:
            raise StopAsyncIteration

        return frame


class UnityManager(WebSocketManager):
    def __init__(self):
        super().__init__(UnityClient, UnitySession)

    async def start_session(self, session_id: str) -> str:
        if not self._clients:
            raise LookupError("No clients connected")

        client_id = next(iter(self._clients.keys()))

        await self.get_client(client_id).start_session(
            session_id,
            BaseWebSocketDTO[BaseStartSessionDTO](
                data=BaseStartSessionDTO(session_id=session_id),
            ),
        )

        return client_id
