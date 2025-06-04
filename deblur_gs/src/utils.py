import hashlib
import hmac
import re
import shutil


def generate_hmac_signature(ts: str, key: str) -> str:
    return hmac.new(key.encode(), ts.encode(), hashlib.sha256).hexdigest()


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
