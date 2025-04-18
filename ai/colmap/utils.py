import os
import subprocess


def set_dir(path):
    if os.path.exists(path):
        os.remove(path)
    else:
        os.makedirs(path, exist_ok=True)

    return path

def get_latest_folder(directory):
    """지정된 디렉토리 내에서 가장 큰 번호를 가진 폴더를 찾습니다."""
    # 디렉토리 내의 모든 폴더들 목록
    folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]

    # 폴더 이름이 숫자 형식일 때, 가장 큰 번호를 찾음
    latest_folder = max(folders, key=lambda x: int(x) if x.isdigit() else -1)
    return latest_folder

def run_colmap(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(f"Error occurred: {stderr.decode('utf-8')}")
    else:
        print(f"Success: {stdout.decode('utf-8')}")