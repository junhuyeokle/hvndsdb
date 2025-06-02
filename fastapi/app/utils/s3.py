from datetime import datetime
import os
from typing import Optional
import zipfile
import aiohttp
import boto3
import botocore
from fastapi.logger import logger
from utils.envs import (
    AWS_ACCESS_KEY,
    AWS_REGION,
    AWS_SECRET_KEY,
    S3_BUCKET_NAME,
    TEMP,
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


async def download_folder_from_presigned_url(url: str, path: str):
    zip_path = os.path.join(TEMP, "temp.zip")

    await download_file_from_presigned_url(url, zip_path)

    logger.info(f"Unzipping\nFrom: {zip_path}\nTo: {path}")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(path)
        logger.info(f"Unzipped\nFrom: {zip_path}\nTo: {path}")

    os.remove(zip_path)


async def download_file_from_presigned_url(url: str, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    logger.info(f"Downloading\nFrom: {url}\nTo: {path}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Download failed")
            with open(path, "wb") as f:
                f.write(await response.read())
    logger.info(f"Downloaded\nFrom: {url}\nTo: {path}")


async def upload_folder_to_presigned_url(url: str, path: str):
    zip_path = os.path.join(TEMP, "temp.zip")

    logger.info(f"Zipping\nFrom: {path}\nTo: {zip_path}")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, path)
                zipf.write(full_path, rel_path)
    logger.info(f"Zipped\nFrom: {path}\nTo: {zip_path}")

    logger.info(f"Uploading\nFrom: {zip_path}\nTo: {url}")
    async with aiohttp.ClientSession() as session:
        with open(zip_path, "rb") as f:
            await session.put(
                url, data=f, headers={"Content-Type": "application/zip"}
            )
    logger.info(f"Uploaded\nFrom: {zip_path}\nTo: {url}")

    os.remove(zip_path)


def is_key_exists(key: str) -> bool:
    try:
        s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=key)
        return True
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            raise


def get_last_modified(key: str) -> Optional[datetime]:
    try:
        response = s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=key)
        return response["LastModified"]
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] in "404":
            return None
