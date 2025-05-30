import os
import zipfile
import aiohttp
import boto3
import botocore
from envs import (
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
    os.makedirs(path, exist_ok=True)

    zip_path = os.path.join(TEMP, "temp.zip")

    print(f"Downloading from {url} to {zip_path}")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Download failed: {response.status}")
                return
            with open(zip_path, "wb") as f:
                f.write(await response.read())
            print(f"Downloaded to: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(path)
        print(f"Extracted to: {path}")

    os.remove(zip_path)


async def download_file_from_presigned_url(url: str, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to download file: {response.status}")
            with open(path, "wb") as f:
                while True:
                    chunk = await response.content.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)


async def upload_folder_to_presigned_url(url: str, path: str):
    zip_path = os.path.join(TEMP, "temp.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, path)
                zipf.write(full_path, rel_path)

    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=600)
    ) as session:
        with open(zip_path, "rb") as f:
            await session.put(
                url, data=f, headers={"Content-Type": "application/zip"}
            )

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
