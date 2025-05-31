import asyncio
import os
from typing import List, Optional
from dtos.base_dto import BaseWebSocketDTO
from dtos.deblur_gs_dto import StartDeblurGSDTO
from managers.web_socket_manager import WebSocketManager
from utils.s3 import get_presigned_download_url, is_key_exists


class DeblurGSManager(WebSocketManager):
    def __init__(self):
        super().__init__()
        self.building_to_client: dict[str, str] = {}
        self.client_to_building: dict[str, str] = {}
        self.building_progress: dict[str, List[str]] = {}
        self.building_progress_conditions: dict[str, asyncio.Condition] = {}

    async def start(
        self,
        building_id: str,
        client_id: Optional[str] = None,
    ):
        if not client_id:
            if not self.active_connections:
                raise ValueError("No client connected to start deblur GS.")
            client_id = next(iter(self.active_connections))

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
        building_id = self.client_to_building.pop(client_id, None)
        self.building_to_client.pop(building_id, None)

        cond = self.building_progress_conditions.setdefault(
            building_id, asyncio.Condition()
        )

        async with cond:
            cond.notify_all()

    async def disconnect(self, client_id: str):
        await super().disconnect(client_id)

        await self.complete(client_id)

    async def update_progress(
        self,
        client_id: str,
        progress: str,
    ):
        if client_id not in self.client_to_building:
            raise ValueError(
                f"Client {client_id} is not associated with any building."
            )

        building_id = self.client_to_building[client_id]

        if building_id not in self.building_progress:
            self.building_progress[building_id] = [progress]
        else:
            self.building_progress[building_id].append(progress)

        cond = self.building_progress_conditions.setdefault(
            building_id, asyncio.Condition()
        )

        async with cond:
            cond.notify_all()

    async def get_progress(self, building_id: str) -> str:
        cond = self.building_progress_conditions.setdefault(
            building_id, asyncio.Condition()
        )

        async with cond:
            await cond.wait()

        return self.building_progress[building_id][-1]

    async def stop(self, building_id: str):
        await self.send(
            self.building_to_client[building_id],
            BaseWebSocketDTO[None](type="stop", data=None),
        )


deblur_gs_manager = DeblurGSManager()
