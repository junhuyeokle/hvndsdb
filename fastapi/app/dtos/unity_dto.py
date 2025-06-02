from pydantic import BaseModel


class StartSessionDTO(BaseModel):
    session_id: str


class SetPlyDTO(BaseModel):
    ply_url: str
    session_id: str


class SetCameraDTO(BaseModel):
    session_id: str
    position: list[float]  # [x, y, z]
    rotation: list[float]  # [x, y, z, w]
