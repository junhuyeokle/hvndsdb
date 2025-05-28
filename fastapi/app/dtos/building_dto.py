from typing import List, Optional
from pydantic import BaseModel
from dtos.base_dto import BaseResponseDTO, TimeMixin
from uuid import UUID


class BuildingDTO(BaseModel):
    building_id: int
    user_id: int
    building_type: Optional[str] = None


class BuildingDetailDTO(BuildingDTO, TimeMixin):
    user_id: Optional[int] = None
    building_type: Optional[str] = None


class AddBuildingRequestDTO(BuildingDetailDTO):
    pass


class UpdateBuildingRequestDTO(BuildingDetailDTO):
    pass


class GetBuildingDetailResponseDTO(BaseResponseDTO[BuildingDetailDTO]):
    pass


class GetBuildingListRequestDTO(BaseModel):
    query: Optional[str] = None


class GetBuildingListResponseDTO(BaseResponseDTO[List[BuildingDTO]]):
    pass
