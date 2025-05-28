import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from dtos.base_dto import BaseWebSocketDTO
from dtos.deblur_gs_dto import DeblurGSCompletedDTO, StartDeblurGSDTO
from services.deblur_gs_service import complete_deblur_gs_service
from web_socket import WebSocketManager


class DeblurGSManager(WebSocketManager):
    def __init__(self):
        super().__init__()
        self.processing_buildings = set()

    def start_deblur_gs(self, client_id: str, building_id: str):
        if building_id in self.processing_buildings:
            return

        self.processing_buildings.add(building_id)

        self.send(
            client_id,
            BaseWebSocketDTO[StartDeblurGSDTO](
                type="start",
                data=StartDeblurGSDTO(building_id=building_id),
            ),
        )

    def complete_deblur_gs(self, building_id: str):
        if building_id not in self.processing_buildings:
            return

        self.processing_buildings.remove(building_id)


deblur_gs_router = APIRouter()

manager = DeblurGSManager()


@deblur_gs_router.websocket("/")
async def deblur_gs_route(ws: WebSocket):
    client_id = ws.client.host
    manager.connect(client_id, ws)

    try:
        while True:
            raw = await ws.receive_text()
            dto = BaseWebSocketDTO(**json.loads(raw))
            if dto.type == "complete":
                complete_deblur_gs_service(
                    dto=DeblurGSCompletedDTO(**dto.data), manager=manager
                )
    except WebSocketDisconnect:
        manager.disconnect(client_id)
