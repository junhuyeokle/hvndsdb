from dtos.analyzer_dto import StartAnalyzerDTO
from managers import analyzer_manager


async def start_service(client_id: str, dto: StartAnalyzerDTO):
    await analyzer_manager.start(dto.building_id, client_id)


async def stop_deblur_gs_service(client_id: str):
    await analyzer_manager.stop_deblur_gs(
        analyzer_manager.get_shared_data(client_id)["building_id"]
    )
