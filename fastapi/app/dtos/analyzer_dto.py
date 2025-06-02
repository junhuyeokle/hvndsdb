from pydantic import BaseModel


class StartAnalyzerDTO(BaseModel):
    building_id: str


class CenterFrameDTO(BaseModel):
    frame_id: str = "center"
    frame: str


class AroundFrameDTO(BaseModel):
    frame_id: str = "around"
    frame: str
