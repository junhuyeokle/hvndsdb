import boto3
from envs import (
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


def get_presigned_upload_url(key):
    return s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": S3_BUCKET_NAME,
            "Key": key,
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
