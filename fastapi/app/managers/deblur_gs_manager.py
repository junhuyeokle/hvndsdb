from managers.web_socket_manager import WebSocketManager
from services.deblur_gs_service import start_service


class DeblurGSManager(WebSocketManager):
    def __init__(self):
        super().__init__()
        self.building_to_client: dict[str, str] = {}
        self.client_to_building: dict[str, str] = {}

    async def start_deblur_gs(self, client_id: str, building_id: str):
        await start_service(
            client_id=client_id, building_id=building_id, manager=self
        )

    def complete_deblur_gs(self, client_id: str):
        building_id = self.client_to_building.pop(client_id, None)
        self.building_to_client.pop(building_id, None)
