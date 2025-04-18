import os
import subprocess


def set_dir(path):
    if os.path.exists(path):
        os.remove(path)
    else:
        os.makedirs(path, exist_ok=True)

    return path

def get_latest_folder(directory):
    folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]

    latest_folder = max(folders, key=lambda x: int(x) if x.isdigit() else -1)
    return latest_folder

def colmap(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(f"Error occurred: {stderr.decode('utf-8')}")
    else:
        print(f"Success: {stdout.decode('utf-8')}")