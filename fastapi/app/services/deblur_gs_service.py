from dtos.deblur_gs_dto import DeblurGSCompletedDTO
from routers.deblur_gs_router import DeblurGSManager


def complete_deblur_gs_service(
    dto: DeblurGSCompletedDTO, manager: DeblurGSManager
):
    manager.complete_deblur_gs(dto.building_id)
