from typing import Optional
from pydantic import BaseModel


class StartDeblurGSDTO(BaseModel):
    frames_url: str
    colmap_url: str
    deblur_gs_url: Optional[str] = None


class UploadDeblurGSDTO(BaseModel):
    deblur_gs_url: str


class UpdateDeblurGSProgressDTO(BaseModel):
    progress: str


class PLYUrlDTO(BaseModel):
    ply_url: str
