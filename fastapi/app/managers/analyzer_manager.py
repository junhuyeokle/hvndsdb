import asyncio
from typing import Dict, Set, Tuple
from dtos.base_dto import BaseWebSocketDTO
from managers.web_socket_manager import WebSocketManager


class AnalyzerManager(WebSocketManager):
    def __init__(self):
        super().__init__()
        self.buildings: Dict[str, Tuple[asyncio.Task, Set[str]]] = {}

    async def start(self, building_id: str, client_id: str):
        if building_id not in self.buildings:
            from workers import analyzer_worker

            self.buildings[building_id] = (
                asyncio.create_task(analyzer_worker.run(building_id)),
                set(),
            )

            def on_done_callback(_, building_id=building_id):
                client_ids = self.buildings.pop(building_id, (None, set()))[1]
                for client_id in client_ids:
                    asyncio.create_task(self.disconnect(client_id))

            self.buildings[building_id][0].add_done_callback(on_done_callback)

        if "building_id" in self.get_shared_data(client_id):
            raise LookupError(
                f"Client {client_id} already has a building associated."
            )

        self.set_shared_data(client_id, "building_id", building_id)
        self.buildings[building_id][1].add(client_id)

    async def stop_deblur_gs(self, building_id: str):
        from managers import deblur_gs_manager

        await deblur_gs_manager.stop(
            deblur_gs_manager.building_to_client[building_id]
        )

    async def update_progress(self, building_id: str, progress: str):
        client_ids = self.buildings.get(building_id, (None, set()))[1]
        for client_id in client_ids:
            await self.send(
                client_id,
                BaseWebSocketDTO[str](
                    type="progress",
                    data=progress,
                ),
            )

    async def disconnect(self, client_id: str):
        shared = self.get_shared_data(client_id)
        building_id = shared.pop("building_id", None)
        if building_id and building_id in self.buildings:
            self.buildings[building_id][1].discard(client_id)

        await super().disconnect(client_id)
