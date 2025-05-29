from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import String
from dtos.base_dto import BaseResponseDTO, TimeMixin
from uuid import UUID


class BuildingDTO(BaseModel):
    building_id: UUID
    name: str
    longitude: float
    latitude: float
    user_id: UUID
    is_ready: bool

    model_config = {"from_attributes": True}


class BuildingDetailDTO(BuildingDTO, TimeMixin):
    pass


class AddBuildingRequestDTO(BaseModel):
    name: str
    longitude: str
    latitude: str
    user_id: str


class UpdateBuildingRequestDTO(BaseModel):
    name: Optional[str] = None
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    user_id: Optional[str] = None


class GetBuildingDetailResponseDTO(BaseResponseDTO[BuildingDetailDTO]):
    pass


class GetBuildingListRequestDTO(BaseModel):
    query: Optional[str] = None


class GetBuildingListResponseDTO(BaseResponseDTO[List[BuildingDTO]]):
    pass
