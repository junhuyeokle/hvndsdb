from typing import List, Optional
from pydantic import BaseModel
from dtos.base_dto import BaseResponseDTO, TimeMixin
from uuid import UUID

from dtos.building_dto import BuildingDTO


class UserDTO(BaseModel):
    user_id: UUID
    email: str
    name: str


class UserDetailDTO(UserDTO, TimeMixin):
    buildings: List[BuildingDTO]


class AddUserRequestDTO(BaseModel):
    email: str
    name: str


class UpdateUserRequestDTO(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None


class GetUserDetailResponseDTO(BaseResponseDTO[UserDetailDTO]):
    pass


class GetUserListRequestDTO(BaseModel):
    query: Optional[str] = None


class GetUserListResponseDTO(BaseResponseDTO[List[UserDTO]]):
    pass
