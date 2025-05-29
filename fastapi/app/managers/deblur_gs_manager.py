from typing import Optional
from managers.web_socket_manager import WebSocketManager
from services.deblur_gs_service import start_service


class DeblurGSManager(WebSocketManager):
    def __init__(self):
        super().__init__()
        self.building_to_client: dict[str, str] = {}
        self.client_to_building: dict[str, str] = {}

    async def start_deblur_gs(
        self,
        building_id: str,
        client_id: Optional[str] = None,
    ):
        if not client_id:
            if not self.active_connections:
                raise ValueError("No client connected to start deblur GS.")
            client_id = next(iter(self.active_connections))
        await start_service(
            client_id=client_id, building_id=building_id, manager=self
        )

    def complete_deblur_gs(self, client_id: str):
        building_id = self.client_to_building.pop(client_id, None)
        self.building_to_client.pop(building_id, None)
