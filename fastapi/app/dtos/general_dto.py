from pydantic import BaseModel

from dtos.base_dto import BaseResponseDTO


class GetPresignedUrlReqeustDTO(BaseModel):
    key: str


class PresignedUrlDTO(BaseModel):
    url: str


class PresignedUrlDetaillDTO(PresignedUrlDTO):
    key: str


class GetPresignedUrlResponseDTO(BaseResponseDTO[PresignedUrlDetaillDTO]):
    pass
