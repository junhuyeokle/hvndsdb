from dtos.base_dto import BaseWebSocketDTO, BaseEndSessionDTO
from dtos.deblur_gs_dto import (
    PLYUrlResponseDTO,
    ProgressDTO,
    UploadDTO,
    PLYUrlRequestDTO,
    CancelSessionCompleteDTO,
    UploadCompleteDTO,
    CompleteDTO,
)
from managers import deblur_gs_manager
from managers.deblur_gs_manager import DeblurGSSession
from utils.s3 import get_presigned_upload_url


async def upload_service(client_id: str, building_id: str):
    await deblur_gs_manager.get_client(client_id).send(
        BaseWebSocketDTO[UploadDTO](
            data=UploadDTO(
                session_id=building_id,
                deblur_gs_url=get_presigned_upload_url(
                    building_id + "/deblur_gs.zip",
                    "application/zip",
                ),
            ),
        ),
    )


async def complete_service(client_id: str, dto: CompleteDTO):
    await upload_service(client_id, dto.session_id)


async def upload_complete_service(client_id: str, dto: UploadCompleteDTO):
    await deblur_gs_manager.get_client(client_id).end_session(
        dto.session_id,
        BaseWebSocketDTO[BaseEndSessionDTO](
            data=BaseEndSessionDTO(session_id=dto.session_id)
        ),
    )


async def progress_service(client_id: str, dto: ProgressDTO):
    session: DeblurGSSession = deblur_gs_manager.get_client(
        client_id
    ).get_session(dto.session_id)
    await session.put_progress(dto.progress)


async def ply_url_request_service(client_id: str, dto: PLYUrlRequestDTO):
    await deblur_gs_manager.get_client(client_id).send(
        BaseWebSocketDTO[PLYUrlResponseDTO](
            data=PLYUrlResponseDTO(
                session_id=dto.session_id,
                ply_url=get_presigned_upload_url(
                    dto.session_id + "/point_cloud.ply",
                    "application/octet-stream",
                ),
            ),
        ),
    )


async def cancel_complete_service(
        client_id: str, dto: CancelSessionCompleteDTO
):
    await upload_service(client_id, dto.session_id)
