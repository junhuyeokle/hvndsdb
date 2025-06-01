from dtos.base_dto import BaseWebSocketDTO
from dtos.deblur_gs_dto import (
    PLYUrlDTO,
    UpdateDeblurGSProgressDTO,
    UploadDeblurGSDTO,
)
from managers.deblur_gs_manager import deblur_gs_manager
from utils.s3 import get_presigned_upload_url


async def upload_service(client_id: str):
    await deblur_gs_manager.send(
        client_id,
        BaseWebSocketDTO[UploadDeblurGSDTO](
            type="upload",
            data=UploadDeblurGSDTO(
                deblur_gs_url=get_presigned_upload_url(
                    deblur_gs_manager.client_to_building[client_id]
                    + "/deblur_gs.zip",
                    "application/zip",
                ),
            ),
        ),
    )


async def complete_service(client_id: str):
    await upload_service(client_id)


async def upload_complete_service(client_id: str):
    await deblur_gs_manager.complete(client_id)


async def update_progress_service(
    client_id: str, dto: UpdateDeblurGSProgressDTO
):
    await deblur_gs_manager.update_progress(client_id, dto.progress)


async def ply_url_service(client_id: str):
    await deblur_gs_manager.send(
        client_id,
        BaseWebSocketDTO[PLYUrlDTO](
            type="ply_url",
            data=PLYUrlDTO(
                ply_url=get_presigned_upload_url(
                    deblur_gs_manager.client_to_building[client_id]
                    + "/point_cloud.ply",
                    "application/octet-stream",
                )
            ),
        ),
    )


async def stop_complete_service(client_id: str):
    await upload_service(client_id)
