import asyncio
from dtos.analyzer_dto import StartAnalyzerDTO
from dtos.base_dto import BaseWebSocketDTO
from managers import analyzer_manager


async def start_service(client_id: str, dto: StartAnalyzerDTO):
    await analyzer_manager.start(dto.building_id, client_id)


async def stop_deblur_gs_service(client_id: str):
    await analyzer_manager.stop_deblur_gs(client_id)
