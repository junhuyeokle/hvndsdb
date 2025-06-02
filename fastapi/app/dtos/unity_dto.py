from pydantic import BaseModel


class StartSessionDTO(BaseModel):
    session_id: str


class StartSessionCompleteDTO(BaseModel):
    session_id: str


class FrameDTO(BaseModel):
    session_id: str
    frame: str


class StopSessionDTO(BaseModel):
    session_id: str


class SetPlyDTO(BaseModel):
    ply_url: str
    session_id: str


class SetCameraPositionDTO(BaseModel):
    session_id: str
    x: float
    y: float
    z: float


class SetCameraRotationDTO(BaseModel):
    session_id: str
    x: float
    y: float
    z: float
    w: float
