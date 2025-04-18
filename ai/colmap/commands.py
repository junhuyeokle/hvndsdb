import os
import struct

from .configs import COLMAP_PATH
from .utils import set_dir, run_colmap, get_latest_folder


def extract_features(frames_path, result_path):
    set_dir(result_path)

    database_path = os.path.join(result_path, "database.db")
    print(database_path)

    command = f"\"{COLMAP_PATH}\" feature_extractor --database_path \"{database_path}\" --image_path \"{frames_path}\""
    run_colmap(command)

def image_matching(result_path):
    database_path = os.path.join(result_path, "database.db")
    command = f"\"{COLMAP_PATH}\" exhaustive_matcher --database_path \"{database_path}\""
    run_colmap(command)

def mapper(frames_path, result_path):
    sparse_path = set_dir(os.path.join(result_path, "sparse"))

    database_path = os.path.join(result_path, "database.db")
    command = f"\"{COLMAP_PATH}\" mapper --database_path \"{database_path}\" --image_path \"{frames_path}\" --output_path \"{sparse_path}\""
    run_colmap(command)

def extract_3d_points_and_6dof(result_path):
    sparse_path = os.path.join(result_path, "sparse")
    lastest_sparse_path = os.path.join(sparse_path, get_latest_folder(sparse_path))

    output_path = os.path.join(result_path, '3d_points.ply')

    command = f"\"{COLMAP_PATH}\" model_converter --input_path \"{lastest_sparse_path}\" --output_path \"{output_path}\" --output_type PLY"
    run_colmap(command)

def extract_camera_poses(result_path):
    sparse_path = os.path.join(result_path, "sparse")
    lastest_sparse_path = os.path.join(sparse_path, get_latest_folder(sparse_path))

    images_file_path = os.path.join(lastest_sparse_path, 'images.bin')

    if not os.path.exists(images_file_path):
        print(f"Error: {images_file_path} does not exist")
        return {}

    poses = {}

    with open(images_file_path, 'rb') as file:
        # 헤더 정보 읽기
        num_images = struct.unpack('Q', file.read(8))[0]  # 이미지 수 (unsigned long long)

        for _ in range(num_images):
            # 각 이미지에 대한 데이터 읽기
            image_id = struct.unpack('Q', file.read(8))[0]  # 이미지 ID
            camera_id = struct.unpack('Q', file.read(8))[0]  # 카메라 ID

            # Rotation quaternion (4개 값) 읽기
            qvec = struct.unpack('4d', file.read(32))  # quaternion (rotation)
            tvec = struct.unpack('3d', file.read(24))  # translation (position)

            # 이름 (이미지 파일명) 읽기
            name_length = struct.unpack('H', file.read(2))[0]  # 이름 길이
            name_bytes = file.read(name_length)  # 바이트로 읽기
            try:
                name = name_bytes.decode('utf-8')  # UTF-8 문자열로 변환
            except UnicodeDecodeError:
                name = name_bytes.decode('latin1')  # `latin1`로 디코딩 시도

            # 포즈 저장 (위치와 회전)
            poses[name] = {
                'image_id': image_id,
                'camera_id': camera_id,
                'position': tvec,  # 위치
                'rotation': qvec  # 회전 (쿼터니언)
            }

    return poses