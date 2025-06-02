import asyncio
import os
from typing import Optional
from dtos.base_dto import BaseWebSocketDTO
from dtos.deblur_gs_dto import StartDeblurGSDTO
from managers.web_socket_manager import WebSocketManager
from utils.s3 import get_presigned_download_url, is_key_exists


class DeblurGSManager(WebSocketManager):
    def __init__(self):
        super().__init__()
        self.building_to_client: dict[str, str] = {}

    async def start(self, building_id: str, client_id: Optional[str] = None):
        if not client_id:
            if not self.connections:
                raise RuntimeError("No client connected to start deblur GS.")
            client_id = next(iter(self.connections))

        if building_id in self.building_to_client:
            raise ValueError(
                f"Building {building_id} is already associated with a client."
            )

        if "building_id" in self.get_shared_data(client_id):
            raise ValueError(
                f"Client {client_id} is already associated with a building."
            )

        self.set_shared_data(client_id, "building_id", building_id)
        self.set_shared_data(client_id, "progress_queue", asyncio.Queue())

        self.building_to_client[building_id] = client_id

        await self.send(
            client_id,
            BaseWebSocketDTO[StartDeblurGSDTO](
                type="start",
                data=StartDeblurGSDTO(
                    frames_url=get_presigned_download_url(
                        building_id + "/frames.zip"
                    ),
                    colmap_url=get_presigned_download_url(
                        building_id + "/colmap.zip"
                    ),
                    deblur_gs_url=(
                        get_presigned_download_url(
                            building_id + "/deblur_gs.zip"
                        )
                        if is_key_exists(
                            os.path.join(building_id, "deblur_gs.zip")
                        )
                        else None
                    ),
                ),
            ),
        )

    async def complete(self, client_id: str):
        shared = self.get_shared_data(client_id)
        building_id = shared.pop("building_id", None)
        progress_queue: asyncio.Queue = shared.pop("progress_queue", None)

        if not building_id or not progress_queue:
            raise LookupError(
                f"Client {client_id} has no building or progress queue."
            )

        await progress_queue.put(None)
        self.building_to_client.pop(building_id, None)

    async def disconnect(self, client_id: str):
        await self.complete(client_id)
        await super().disconnect(client_id)

    async def update_progress(self, client_id: str, progress: str):
        shared = self.get_shared_data(client_id)
        progress_queue: asyncio.Queue = shared.get("progress_queue")

        if not progress_queue:
            raise LookupError(
                f"Client {client_id} has no active progress queue."
            )

        await progress_queue.put(progress)

    async def get_progress(self, client_id: str):
        progress_queue: asyncio.Queue = self.get_shared_data(client_id).get(
            "progress_queue"
        )

        if not progress_queue:
            raise LookupError(
                f"Client {client_id} has no active progress queue."
            )

        progress = await progress_queue.get()

        if progress is None:
            raise StopAsyncIteration

        return progress

    async def stop(self, client_id: str):
        await self.send(
            client_id,
            BaseWebSocketDTO[None](type="stop", data=None),
        )
