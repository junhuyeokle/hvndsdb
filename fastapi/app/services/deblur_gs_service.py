from dtos.base_dto import BaseWebSocketDTO
from dtos.deblur_gs_dto import StartDeblurGSDTO, UploadDeblurGSDTO
from sc3 import get_presigned_download_url, get_presigned_upload_url


async def start_service(client_id: str, building_id: str, manager):
    if building_id in manager.building_to_client:
        return

    if client_id in manager.client_to_building:
        return

    manager.building_to_client[building_id] = client_id
    manager.client_to_building[client_id] = building_id

    await manager.send(
        client_id,
        BaseWebSocketDTO[StartDeblurGSDTO](
            type="start",
            data=StartDeblurGSDTO(
                frames_url=get_presigned_download_url(building_id + "/frames"),
                colmap_url=get_presigned_download_url(building_id + "/colmap"),
                # deblur_gs_url=get_presigned_download_url(
                #     building_id + "/deblur_gs"
                # ),
            ),
        ),
    )


async def complete_service(client_id: str, manager):
    await manager.send(
        client_id,
        BaseWebSocketDTO[UploadDeblurGSDTO](
            type="upload",
            data=UploadDeblurGSDTO(
                deblur_gs_url=get_presigned_upload_url(
                    manager.client_to_building[client_id] + "/deblur_gs"
                ),
            ),
        ),
    )


def upload_complete_service(client_id: str, manager):
    manager.complete_deblur_gs(client_id=client_id)
