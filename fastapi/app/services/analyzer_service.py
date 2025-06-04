from dtos.analyzer_dto import CancelDeblurGS
from dtos.base_dto import BaseStartSessionDTO
from managers import analyzer_manager, deblur_gs_manager


def start_session_service(dto: BaseStartSessionDTO):
    analyzer_manager.start_analyzer(dto.session_id)


async def cancel_deblur_gs_service(dto: CancelDeblurGS):
    await deblur_gs_manager.cancel_session(dto.session_id)
