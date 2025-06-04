import os
import uuid
import zipfile

import aiohttp


async def upload_folder_to_presigned_url(url: str, path: str, temp: str):
    zip_path = os.path.join(temp, uuid.uuid4().hex + ".zip")

    print(f"Zipping\nFrom: {path}\nTo: {zip_path}")
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, path)
                zipf.write(full_path, rel_path)
    print(f"Zipped\nFrom: {path}\nTo: {zip_path}")

    await upload_file_to_presigned_url(url, zip_path, "application/zip")

    os.remove(zip_path)


async def upload_file_to_presigned_url(url: str, path: str, content_type: str):
    print(f"Uploading\nFrom: {path}\nTo: {url}")
    async with aiohttp.ClientSession() as session:
        with open(path, "rb") as f:
            response = await session.put(
                url,
                data=f,
                headers={"Content-Type": content_type},
            )
            if response.status != 200:
                raise Exception(f"Upload failed: {await response.text()}")
    print(f"Uploaded\nFrom: {path}\nTo: {url}")


async def download_folder_from_presigned_url(url: str, path: str, temp: str):
    zip_path = os.path.join(temp, uuid.uuid4().hex + ".zip")

    await download_file_from_presigned_url(url, zip_path)

    print(f"Unzipping\nFrom: {zip_path}\nTo: {path}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with zipfile.ZipFile(zip_path) as zip_ref:
        zip_ref.extractall(path)
    print(f"Unzipped\nFrom: {zip_path}\nTo: {path}")

    os.remove(zip_path)


async def download_file_from_presigned_url(url: str, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    print(f"Downloading\nFrom: {url}\nTo: {path}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Download failed")
            with open(path, "wb") as f:
                f.write(await response.read())
    print(f"Downloaded\nFrom: {url}\nTo: {path}")
