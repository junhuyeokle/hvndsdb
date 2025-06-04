from typing import ClassVar

from dtos.base_dto import BaseSessionDataDTO


class StopDeblurGSDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "stop_deblur_gs"


class CenterFrameDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "center_frame"
    frame: str


class AroundFrameDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "around_frame"
    frame: str


class ProgressDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "progress"
    progress: str
