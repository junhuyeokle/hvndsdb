from typing import List, Optional
from pydantic import BaseModel
from dtos.base_dto import BaseResponseDTO, TimeMixin
from uuid import UUID


class UserDTO(BaseModel):
    user_id: UUID
    email: str
    name: str


class UserDetailDTO(UserDTO, TimeMixin):
    pass


class AddUserRequestDTO(UserDetailDTO):
    email: str
    name: str


class UpdateUserRequestDTO(UserDetailDTO):
    pass


class GetUserDetailResponseDTO(BaseResponseDTO[UserDetailDTO]):
    pass


class GetUserListRequestDTO(BaseModel):
    query: Optional[str] = None


class GetUserListResponseDTO(BaseResponseDTO[List[UserDTO]]):
    pass
