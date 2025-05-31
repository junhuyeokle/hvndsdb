from pydantic import BaseModel


class StartAnalyzerDTO(BaseModel):
    building_id: str
