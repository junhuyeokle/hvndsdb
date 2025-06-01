from asyncio import Task
import asyncio
from dtos.base_dto import BaseWebSocketDTO
from managers.web_socket_manager import WebSocketManager


class AnalyzerManager(WebSocketManager):
    def __init__(self):
        super().__init__()

    async def start(self, building_id: str, client_id: str):
        if "building_id" in self.get_shared_data(client_id):
            raise ValueError(
                f"Client {client_id} is already associated with a building."
            )

        self.set_shared_data(client_id, "building_id", building_id)

        from workers import analyzer_worker

        task = asyncio.create_task(analyzer_worker.run(client_id))

        self.set_shared_data(client_id, "task", task)

    async def stop_deblur_gs(self, client_id: str):
        building_id = self.get_shared_data(client_id).get("building_id")
        if not building_id:
            raise LookupError(f"Client {client_id} has no associated building.")
        from managers import deblur_gs_manager

        await deblur_gs_manager.stop(
            deblur_gs_manager.building_to_client[building_id]
        )

    async def update_progress(self, client_id: str, progress: str):
        await self.send(
            client_id,
            BaseWebSocketDTO[str](
                type="progress",
                data=progress,
            ),
        )

    async def disconnect(self, client_id: str):
        shared = self.get_shared_data(client_id)
        shared.pop("building_id", None)
        task: Task = shared.pop("task", None)

        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        await super().disconnect(client_id)
