from typing import Generic, Optional, TypeVar, ClassVar

from pydantic import BaseModel, validator


class BaseDataDTO(BaseModel):
    def get_type(self) -> Optional[str]:
        return getattr(self.__class__, "type", None)


T = TypeVar("T", bound=BaseDataDTO)


class BaseWebSocketDTO(BaseModel, Generic[T]):
    data: Optional[T] = None
    type: str = ""

    @validator("type", always=True, pre=True)
    def set_type_from_data(cls, v, values):
        data = values.get("data")
        if v:
            return v
        if data and hasattr(data, "get_type"):
            return data.get_type()
        return ""


class BaseSessionDataDTO(BaseDataDTO):
    session_id: str


class BaseStartSessionDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "start_session"


class BaseReadyDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "ready"


class BaseEndSessionDTO(BaseSessionDataDTO):
    type: ClassVar[str] = "end_session"


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
