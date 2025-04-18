import os

from .configs import COLMAP_PATH
from .utils import set_dir, run_colmap, get_latest_folder


def extract(frames_path, result_path):
    set_dir(result_path)
    database_path = os.path.join(result_path, "database.db")

    command = f"\"{COLMAP_PATH}\" feature_extractor " \
              f"--database_path \"{database_path}\" " \
              f"--image_path \"{frames_path}\""
    run_colmap(command)


def match(result_path):
    database_path = os.path.join(result_path, "database.db")

    command = f"\"{COLMAP_PATH}\" exhaustive_matcher " \
              f"--database_path \"{database_path}\""
    run_colmap(command)


def pair(frames_path, result_path):
    sparse_path = set_dir(os.path.join(result_path, "sparse"))
    database_path = os.path.join(result_path, "database.db")

    command = f"\"{COLMAP_PATH}\" mapper " \
              f"--database_path \"{database_path}\" " \
              f"--image_path \"{frames_path}\" " \
              f"--output_path \"{sparse_path}\""
    run_colmap(command)


def convert(result_path):
    sparse_path = os.path.join(result_path, "sparse")
    lastest_sparse_path = os.path.join(sparse_path, get_latest_folder(sparse_path))

    command = f"\"{COLMAP_PATH}\" model_converter " \
              f"--input_path \"{lastest_sparse_path}\" " \
              f"--output_path \"{lastest_sparse_path}\" " \
              f"--output_type TXT"
    run_colmap(command)


def extract_3d_points_and_6dof(result_path):
    sparse_path = os.path.join(result_path, "sparse")
    lastest_sparse_path = os.path.join(sparse_path, get_latest_folder(sparse_path))
    output_path = os.path.join(result_path, '3d_points.ply')

    command = f"\"{COLMAP_PATH}\" model_converter " \
              f"--input_path \"{lastest_sparse_path}\" " \
              f"--output_path \"{output_path}\" " \
              f"--output_type PLY"
    run_colmap(command)


def extract_camera_poses(result_path):
    sparse_path = os.path.join(result_path, "sparse")
    lastest_sparse_path = os.path.join(sparse_path, get_latest_folder(sparse_path))

    images_file_path = os.path.join(lastest_sparse_path, 'images.txt')

    poses = {}

    with open(images_file_path, 'r') as file:
        flag = False

        lines = file.readlines()
        for line in lines:
            if flag:
                flag = False
                continue
            if line.startswith('#'):
                continue

            data = line.split()
            if len(data) >= 10:
                image_id = int(data[0])
                qw, qx, qy, qz = map(float, data[1:5])
                tx, ty, tz = map(float, data[5:8])
                camera_id = int(data[8])
                image_name = data[9]

                poses[image_name] = {
                    'image_id': image_id,
                    'camera_id': camera_id,
                    'rotation': (qw, qx, qy, qz),  # 회전 (quaternion)
                    'position': (tx, ty, tz)  # 위치 (translation)
                }

            flag = True

    return poses
