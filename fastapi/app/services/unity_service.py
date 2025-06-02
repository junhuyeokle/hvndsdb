from dtos.unity_dto import FrameDTO, StartSessionCompleteDTO
from managers import unity_manager


def start_session_complete_service(dto: StartSessionCompleteDTO):
    unity_manager.start_session_completes[dto.session_id].set()


async def update_frame_service(dto: FrameDTO):
    await unity_manager.update_frame(dto.session_id, dto.frame)
