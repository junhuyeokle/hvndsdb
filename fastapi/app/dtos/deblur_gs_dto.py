from typing import Optional, ClassVar

from dtos.base_dto import (
    BaseStartSessionDTO,
    BaseSessionDataDTO,
)


class StartSessionDTO(BaseStartSessionDTO):
    frames_url: str
    colmap_url: str
    deblur_gs_url: Optional[str] = None


class CancelSessionDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "cancel_session"


class CancelSessionCompleteDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "cancel_session_complete"


class UploadDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "upload"
    deblur_gs_url: str


class UploadCompleteDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "upload_complete"


class ProgressDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "progress"
    progress: str


class PLYUrlRequestDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "ply_url_request"


class PLYUrlResponseDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "ply_url_response"
    ply_url: str


class CompleteDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "complete"
