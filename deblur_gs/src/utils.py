import hashlib
import hmac
import os
import zipfile
import aiohttp

from envs import TEMP


def generate_hmac_signature(ts: str, key: str) -> str:
    return hmac.new(key.encode(), ts.encode(), hashlib.sha256).hexdigest()


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


async def upload_folder_to_presigned_url(url: str, path: str):
    print(f"Uploading folder {path} to {url}")

    zip_path = os.path.join(TEMP, "temp.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, path)
                zipf.write(full_path, rel_path)
        print(f"Created zip file: {zip_path}")

    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=600)
    ) as session:
        with open(zip_path, "rb") as f:
            response = await session.put(
                url, data=f, headers={"Content-Type": "application/zip"}
            )
            if response.status != 200:
                raise Exception(f"Upload failed: {await response.text()}")
        print(f"Uploaded {zip_path} to {url}")

    os.remove(zip_path)
