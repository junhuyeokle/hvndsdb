from pydantic import BaseModel


class StartDeblurGSDTO(BaseModel):
    building_id: str


class DeblurGSCompletedDTO(BaseModel):
    building_id: str
