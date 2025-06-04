import asyncio

from dtos.analyzer_dto import (
    AroundFrameDTO,
    CenterFrameDTO,
    ProgressDTO,
)
from dtos.base_dto import BaseWebSocketDTO
from managers.web_socket_manager import (
    WebSocketManager,
    WebsocketSession,
    WebsocketClient,
)
from tasks import analyzer_task


class AnalyzerClient(WebsocketClient):
    async def update_progress(self, building_id: str, progress: str):
        await self.send(
            BaseWebSocketDTO[ProgressDTO](
                data=ProgressDTO(progress=progress, session_id=building_id)
            )
        )

    async def update_center_frame(self, building_id: str, frame: str):
        await self.send(
            BaseWebSocketDTO[CenterFrameDTO](
                data=CenterFrameDTO(frame=frame, session_id=building_id)
            )
        )

    async def update_around_frame(self, building_id: str, frame: str):
        await self.send(
            BaseWebSocketDTO[AroundFrameDTO](
                data=AroundFrameDTO(frame=frame, session_id=building_id)
            )
        )


class AnalyzerSession(WebsocketSession):
    def __init__(self, session_id: str, client: AnalyzerClient):
        super().__init__(session_id, client)
        self.set_ready()


class AnalyzerManager(WebSocketManager):
    def __init__(self):
        super().__init__(AnalyzerClient, AnalyzerSession)
        self._analyzers: dict[str, asyncio.Task] = {}

    def start_analyzer(self, building_id: str):
        if building_id in self._analyzers:
            raise LookupError(f"Analyzer {building_id} already exists")

        self._analyzers[building_id] = asyncio.create_task(
            analyzer_task.run(building_id)
        )

    def get_analyzer(self, building_id: str) -> asyncio.Task:
        analyzer = self._analyzers.get(building_id)
        if not analyzer:
            raise LookupError(f"No analyzer found {building_id}")

        return analyzer

    async def end_analyzer(self, building_id: str):
        analyzer = self._analyzers.pop(building_id)
        if not analyzer:
            raise LookupError(f"No analyzer found {building_id}")

        self._analyzers[building_id].cancel()
        await self._analyzers[building_id]

    async def update_progress(self, building_id: str, progress: str):
        for client in self._clients.values():
            if not client.has_session(building_id):
                await client.update_progress(building_id, progress)

    async def update_center_frame(self, building_id: str, frame: str):
        for client in self._clients.values():
            if not client.has_session(building_id):
                await client.update_center_frame(building_id, frame)

    async def update_around_frame(self, building_id: str, frame: str):
        for client in self._clients.values():
            if not client.has_session(building_id):
                await client.update_around_frame(building_id, frame)
