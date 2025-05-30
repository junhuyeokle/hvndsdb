import asyncio
import hashlib
import hmac
import os
import re
import shutil
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

    async with aiohttp.ClientSession() as session:
        with open(zip_path, "rb") as f:
            response = await session.put(
                url, data=f, headers={"Content-Type": "application/zip"}
            )
            if response.status != 200:
                raise Exception(f"Upload failed: {await response.text()}")
        print(f"Uploaded {zip_path} to {url}")

    os.remove(zip_path)


async def upload_file_to_presigned_url(url: str, path: str, content_type: str):
    print(f"Uploading file {path} to {url}")

    async with aiohttp.ClientSession() as session:
        with open(path, "rb") as f:
            response = await session.put(
                url,
                data=f,
                headers={"Content-Type": content_type},
            )
            if response.status != 200:
                raise Exception(f"Upload failed: {await response.text()}")
        print(f"Uploaded {path} to {url}")


import os


def get_last_point_cloud(base_path: str):
    try:
        subdirs = []
        for name in os.listdir(base_path):
            full_path = os.path.join(base_path, name)
            if os.path.isdir(full_path):
                parts = name.rsplit("_", 1)
                if len(parts) == 2 and parts[1].isdigit():
                    subdirs.append((int(parts[1]), full_path))

        if not subdirs:
            return None

        subdirs.sort(key=lambda x: x[0])
        return subdirs[-1][1]
    except FileNotFoundError:
        return None


def get_last_checkpoint(folder_path: str) -> int | None:
    try:
        pattern = re.compile(r"^chkpnt(\d+)\.pth$")
        numbers = []

        for filename in os.listdir(folder_path):
            match = pattern.match(filename)
            if match:
                number = int(match.group(1))
                numbers.append(number)

        if not numbers:
            return None

        return max(numbers)
    except FileNotFoundError:
        return None


def clean_deblur_gs(path: str):
    chk_pattern = re.compile(r"^chkpnt(\d+)\.pth$")
    chkpnts = []

    for f in os.listdir(path):
        match = chk_pattern.match(f)
        if match:
            chkpnts.append((int(match.group(1)), f))

    if chkpnts:
        chkpnts.sort()
        keep = chkpnts[-1][1]
        for _, f in chkpnts[:-1]:
            os.remove(os.path.join(path, f))
        print(f"keep: {keep}")

    for f in os.listdir(path):
        if f.startswith("events.out."):
            os.remove(os.path.join(path, f))

    pcloud = os.path.join(path, "point_cloud")
    if os.path.isdir(pcloud):
        shutil.rmtree(pcloud)
