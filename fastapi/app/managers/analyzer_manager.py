from asyncio import Task
import asyncio
from managers.deblur_gs_manager import deblur_gs_manager
from managers.web_socket_manager import WebSocketManager
from workers import analyzer


class AnalyzerManager(WebSocketManager):
    def __init__(self):
        super().__init__()
        self.building_to_client: dict[str, str] = {}
        self.client_to_building: dict[str, str] = {}
        self.client_to_task: dict[str, Task] = {}
        self.building_to_task: dict[str, Task] = {}

    async def start(
        self,
        building_id: str,
        client_id: str,
    ):
        if building_id in self.building_to_client:
            raise ValueError(
                f"Building {building_id} is already associated with a client."
            )

        if client_id in self.client_to_building:
            raise ValueError(
                f"Client {client_id} is already associated with a building."
            )

        self.building_to_client[building_id] = client_id
        self.client_to_building[client_id] = building_id

        self.client_to_task[client_id] = asyncio.create_task(
            analyzer.run(building_id=building_id)
        )
        self.building_to_task[building_id] = self.client_to_task[client_id]

    async def stop_deblur_gs(
        self,
        client_id: str,
    ):
        await deblur_gs_manager.stop(
            building_id=self.client_to_building[client_id]
        )

    async def disconnect(self, client_id: str):
        await super().disconnect(client_id)

        self.client_to_task[client_id].cancel()
        try:
            await self.client_to_task[client_id]
        except asyncio.CancelledError:
            pass

        self.building_to_task.pop(self.client_to_building[client_id], None)
        self.client_to_task.pop(client_id, None)

        self.building_to_client.pop(
            self.client_to_building.pop(client_id, None), None
        )


analyzer_manager = AnalyzerManager()
