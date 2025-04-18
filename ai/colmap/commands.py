import os

from .configs import COLMAP_PATH
from .utils import set_dir, colmap, get_latest_folder


def extract(frames_path, result_path):
    set_dir(result_path)
    database_path = os.path.join(result_path, "database.db")

    command = f"\"{COLMAP_PATH}\" feature_extractor " \
              f"--database_path \"{database_path}\" " \
              f"--image_path \"{frames_path}\""
    colmap(command)


def match(result_path):
    database_path = os.path.join(result_path, "database.db")

    command = f"\"{COLMAP_PATH}\" exhaustive_matcher " \
              f"--database_path \"{database_path}\""
    colmap(command)


def pair(frames_path, result_path):
    sparse_path = set_dir(os.path.join(result_path, "sparse"))
    database_path = os.path.join(result_path, "database.db")

    command = f"\"{COLMAP_PATH}\" mapper " \
              f"--database_path \"{database_path}\" " \
              f"--image_path \"{frames_path}\" " \
              f"--output_path \"{sparse_path}\""
    colmap(command)


def convert(result_path):
    sparse_path = os.path.join(result_path, "sparse")
    lastest_sparse_path = os.path.join(sparse_path, get_latest_folder(sparse_path))

    command = f"\"{COLMAP_PATH}\" model_converter " \
              f"--input_path \"{lastest_sparse_path}\" " \
              f"--output_path \"{lastest_sparse_path}\" " \
              f"--output_type TXT"
    colmap(command)

def parse_images(result_path):
    sparse_path = os.path.join(result_path, "sparse")
    lastest_sparse_path = os.path.join(sparse_path, get_latest_folder(sparse_path))

    images_file_path = os.path.join(lastest_sparse_path, 'images.txt')

    poses = {}

    with open(images_file_path, 'r') as file:
        is_point_2d = False

        lines = file.readlines()
        for line in lines:
            if line.startswith('#'):
                continue

            if is_point_2d:
                is_point_2d = False
                continue

            data = line.split()
            if len(data) >= 10:
                image_id = int(data[0])
                qw, qx, qy, qz = map(float, data[1:5])
                tx, ty, tz = map(float, data[5:8])
                image_name = data[9]

                poses[image_name] = {
                    'image_id': image_id,
                    'rotation': (qw, qx, qy, qz),
                    'position': (tx, ty, tz)
                }

            is_point_2d = True

    return poses

def parse_points(result_path):
    sparse_path = os.path.join(result_path, "sparse")
    lastest_sparse_path = os.path.join(sparse_path, get_latest_folder(sparse_path))

    points_path = os.path.join(lastest_sparse_path, 'points3D.txt')

    points = []

    with open(points_path, 'r') as file:
        lines = file.readlines()

        for line in lines:
            if line.startswith('#'):
                continue

            data = line.split(' ')

            point_id = int(data[0])
            x, y, z = float(data[1]), float(data[2]), float(data[3])
            r, g, b = int(data[4]), int(data[5]), int(data[6])
            error = float(data[7])

            points.append({
                'point_id': point_id,
                'xyz': (x, y, z),
                'color': (r, g, b),
                'error': error,
            })

    return points