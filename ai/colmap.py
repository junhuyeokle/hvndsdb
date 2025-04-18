import subprocess
import os

def run_colmap(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(f"Error occurred: {stderr.decode('utf-8')}")
    else:
        print(f"Success: {stdout.decode('utf-8')}")

def extract_features(colmap_path, frames_path, result_path):
    if os.path.exists(result_path):
        os.remove(result_path)  # 파일 삭제
    else:
        os.makedirs(result_path, exist_ok=True)  # 디렉토리 없으면 생성

    database_path = os.path.join(result_path, "database.db")
    print(database_path)

    command = f"\"{colmap_path}\" feature_extractor --database_path \"{database_path}\" --image_path \"{frames_path}\""
    run_colmap(command)

    image_matching(colmap_path, database_path)

    mapper(colmap_path, frames_path, database_path, result_path)

def image_matching(colmap_path, database_path):
    command = f"\"{colmap_path}\" exhaustive_matcher --database_path \"{database_path}\""
    run_colmap(command)

def mapper(colmap_path, frames_path, database_path, result_path):
    output_path = os.path.join(result_path, "sparse")
    if os.path.exists(output_path):
        os.remove(output_path)  # 파일 삭제
    else:
        os.makedirs(output_path, exist_ok=True)  # 디렉토리 없으면 생성
    command = f"\"{colmap_path}\" mapper --database_path \"{database_path}\" --image_path \"{frames_path}\" --output_path \"{output_path}\""
    run_colmap(command)

def extract_3d_points_and_6dof(colmap_path, database_path):
    model_path = os.path.join(os.path.dirname(database_path), 'sparse')
    output_path = os.path.join(os.path.dirname(database_path), '3d_points.ply')

    command = f"\"{colmap_path}\" model_converter --input_path \"{model_path}\" --output_path \"{output_path}\" --output_type PLY"
    run_colmap(command)

    # 6DoF 추출
    camera_poses = extract_camera_poses(model_path)

    # 6DoF 출력
    for image_id, pose in camera_poses.items():
        print(f"Image {image_id}: Position = {pose['position']}, Rotation = {pose['rotation']}")

# 카메라 위치와 회전 추출 함수 (텍스트 형식으로 저장된 sparse 모델에서)
def extract_camera_poses(model_path):
    poses = {}
    with open(os.path.join(model_path, 'cameras.txt'), 'r') as file:
        lines = file.readlines()
        # 카메라 정보 추출
        for line in lines:
            if line.startswith('#'):
                continue
            data = line.split()
            if len(data) == 7:  # image_id, position, rotation
                image_id = int(data[0])
                position = [float(data[1]), float(data[2]), float(data[3])]
                rotation = [float(data[4]), float(data[5]), float(data[6])]
                poses[image_id] = {"position": position, "rotation": rotation}
    return poses
