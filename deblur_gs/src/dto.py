from typing import Generic, Optional, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class BaseWebSocketDTO(GenericModel, Generic[T]):
    type: str
    data: Optional[T] = None


class StartDeblurGSDTO(BaseModel):
    frames_url: str
    colmap_url: str


class UploadDeblurGSDTO(BaseModel):
    deblur_gs_url: str


class UpdateDeblurGSProgressDTO(BaseModel):
    progress: str


class PLYUrlDTO(BaseModel):
    ply_url: str
