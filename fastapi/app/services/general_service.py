from dtos.general_dto import GetPresignedUrlResponseDTO
from sc3 import get_presigned_url


def get_presigned_url_service(dto):
    if not dto.key:
        raise ValueError("Key must be provided for presigned URL generation.")

    url = get_presigned_url(dto.key)
    return GetPresignedUrlResponseDTO(url=url)
