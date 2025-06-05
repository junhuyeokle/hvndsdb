from datetime import datetime

import boto3

from utils.envs import (
    AWS_ACCESS_KEY,
    AWS_REGION,
    AWS_SECRET_KEY,
    S3_BUCKET_NAME,
)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)


def get_presigned_upload_url(key, content_type) -> str:
    return s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": S3_BUCKET_NAME,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=300,
    )


def get_presigned_download_url(key: str) -> str:
    return s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": S3_BUCKET_NAME,
            "Key": key,
        },
        ExpiresIn=300,
    )


def is_key_exists(key: str) -> bool:
    try:
        s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=key)
        return True
    except Exception:
        return False


def get_last_modified(key: str) -> datetime | None:
    try:
        response = s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=key)
        return response["LastModified"]
    except Exception:
        return None
