from typing import ClassVar

from dtos.base_dto import BaseSessionDataDTO


class CancelSessionDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "cancel_session"


class FrameDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "frame"
    frame: str


class SetPlyDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "set_ply"
    ply_url: str


class SetCameraPositionDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "set_camera_position"
    x: float
    y: float
    z: float


class SetCameraRotationDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "set_camera_rotation"
    x: float
    y: float
    z: float
    w: float
