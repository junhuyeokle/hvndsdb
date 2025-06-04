import hashlib
import hmac
import re
import shutil
import uuid
import zipfile

import aiohttp

from envs import TEMP


def generate_hmac_signature(ts: str, key: str) -> str:
    return hmac.new(key.encode(), ts.encode(), hashlib.sha256).hexdigest()


async def download_folder_from_presigned_url(url: str, path: str):
    zip_path = os.path.join(TEMP, uuid.uuid4().hex + ".zip")

    print(f"Downloading\nFrom: {url}\nTo: {zip_path}")

    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Download failed")
            with open(zip_path, "wb") as f:
                f.write(await response.read())
            print(f"Downloaded\nFrom: {url}\nTo: {zip_path}")

    print(f"Unzipping\nFrom: {zip_path}\nTo: {path}")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(path)
        print(f"Unzipped\nFrom: {zip_path}\nTo: {path}")

    os.remove(zip_path)


async def upload_folder_to_presigned_url(url: str, path: str):
    zip_path = os.path.join(TEMP, uuid.uuid4().hex + ".zip")

    print(f"Zipping\nFrom: {path}\nTo: {zip_path}")
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


import os


def get_last_ply_folder(ply_path: str):
    try:
        sub_dirs = []
        for name in os.listdir(ply_path):
            full_path = os.path.join(ply_path, name)
            if os.path.isdir(full_path):
                parts = name.rsplit("_", 1)
                if len(parts) == 2 and parts[1].isdigit():
                    sub_dirs.append((int(parts[1]), full_path))

        if not sub_dirs:
            return None

        sub_dirs.sort(key=lambda x: x[0])
        return sub_dirs[-1][1]
    except FileNotFoundError:
        return None


def get_last_checkpoint(folder_path: str):
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
        for _, f in chkpnts[:-1]:
            os.remove(os.path.join(path, f))

    for f in os.listdir(path):
        if f.startswith("events.out."):
            os.remove(os.path.join(path, f))

    pcloud = os.path.join(path, "point_cloud")
    if os.path.isdir(pcloud):
        shutil.rmtree(pcloud)
