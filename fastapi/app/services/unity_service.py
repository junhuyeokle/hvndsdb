from dtos.base_dto import BaseEndSessionDTO, BaseReadyDTO
from dtos.unity_dto import FrameDTO
from managers import unity_manager
from managers.unity_manager import UnitySession


async def ready_service(client_id: str, dto: BaseReadyDTO):
    await unity_manager.get_client(client_id).end_session(
        dto.session_id, BaseEndSessionDTO(session_id=dto.session_id)
    )


async def frame_service(client_id: str, dto: FrameDTO):
    session: UnitySession = unity_manager.get_client(client_id).get_session(
        dto.session_id
    )
    await session.put_frame(dto.frame)
