from dtos.base_dto import BaseWebSocketDTO
from dtos.deblur_gs_dto import (
    UpdateDeblurGSProgressDTO,
    UploadDeblurGSDTO,
)
from s3 import get_presigned_upload_url


async def complete_service(client_id: str, manager):
    await manager.send(
        client_id,
        BaseWebSocketDTO[UploadDeblurGSDTO](
            type="upload",
            data=UploadDeblurGSDTO(
                deblur_gs_url=get_presigned_upload_url(
                    manager.client_to_building[client_id] + "/deblur_gs.zip",
                    "application/zip",
                ),
            ),
        ),
    )


def upload_complete_service(client_id: str, manager):
    manager.complete(client_id=client_id)


def update_progress_service(
    client_id: str, dto: UpdateDeblurGSProgressDTO, manager
):
    manager.update_progress(
        client_id=client_id,
        progress=dto.progress,
    )
