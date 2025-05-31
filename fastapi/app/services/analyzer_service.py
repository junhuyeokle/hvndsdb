from dtos.analyzer_dto import StartAnalyzerDTO
from managers.analyzer_manager import analyzer_manager


async def start_service(client_id: str, dto: StartAnalyzerDTO):
    await analyzer_manager.start(
        building_id=dto.building_id, client_id=client_id
    )


async def stop_deblur_gs_service(client_id: str):
    await analyzer_manager.stop_deblur_gs(client_id=client_id)
