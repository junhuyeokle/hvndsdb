from asyncio import Task
import asyncio
from managers.deblur_gs_manager import deblur_gs_manager
from managers.web_socket_manager import WebSocketManager
from workers import analyzer


class AnalyzerManager(WebSocketManager):
    def __init__(self):
        super().__init__()
        self.building_to_client: dict[str, str] = {}

    async def start(self, building_id: str, client_id: str):
        if building_id in self.building_to_client:
            raise ValueError(
                f"Building {building_id} is already associated with a client."
            )

        if "building_id" in self.get_shared_data(client_id):
            raise ValueError(
                f"Client {client_id} is already associated with a building."
            )

        self.set_shared_data(client_id, "building_id", building_id)

        self.building_to_client[building_id] = client_id

        progress_queue = asyncio.Queue()
        task = asyncio.create_task(analyzer.run(building_id=building_id))

        self.set_shared_data(client_id, "task", task)
        self.set_shared_data(client_id, "progress_queue", progress_queue)

    async def stop_deblur_gs(self, client_id: str):
        building_id = self.get_shared_data(client_id).get("building_id")
        if not building_id:
            raise LookupError(f"Client {client_id} has no associated building.")
        await deblur_gs_manager.stop(
            deblur_gs_manager.building_to_client[building_id]
        )

    async def update_progress(self, client_id: str, progress: str):
        queue: asyncio.Queue = self.get_shared_data(client_id).get(
            "progress_queue"
        )
        if not queue:
            raise LookupError(f"Client {client_id} has no progress queue.")

        await queue.put(progress)

    async def get_progress(self, client_id: str):
        queue: asyncio.Queue = self.get_shared_data(client_id).get(
            "progress_queue"
        )

        if not queue:
            raise LookupError(f"Client {client_id} has no progress queue.")

        progress = await queue.get()

        if progress == "__COMPLETE__":
            raise StopAsyncIteration

    async def disconnect(self, client_id: str):
        shared = self.get_shared_data(client_id)
        building_id = shared.get("building_id")
        task: Task = shared.get("task")

        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        if building_id:
            self.building_to_client.pop(building_id, None)

        await super().disconnect(client_id)


analyzer_manager = AnalyzerManager()
