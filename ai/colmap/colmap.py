import os

import pycolmap

from .configs import COLMAP_PATH
from .utils import set_dir, command, get_latest_folder


def reconstruct(result_path, frames_path):
    reconstruction = pycolmap.incremental_mapping(
        database_path=os.path.join(result_path, "database.db"),
        image_path=frames_path,
        output_path=os.path.join(result_path, "sparse"),
    )
    return reconstruction


def extract(frames_path, result_path):
    set_dir(result_path)
    database_path = os.path.join(result_path, "database.db")

    cmd = f"\"{COLMAP_PATH}\" feature_extractor " \
              f"--database_path \"{database_path}\" " \
              f"--image_path \"{frames_path}\""
    command(cmd)


def match(result_path):
    database_path = os.path.join(result_path, "database.db")

    cmd = f"\"{COLMAP_PATH}\" exhaustive_matcher " \
              f"--database_path \"{database_path}\""
    command(cmd)


def pair(frames_path, result_path):
    sparse_path = set_dir(os.path.join(result_path, "sparse"))
    database_path = os.path.join(result_path, "database.db")

    cmd = f"\"{COLMAP_PATH}\" mapper " \
              f"--database_path \"{database_path}\" " \
              f"--image_path \"{frames_path}\" " \
              f"--output_path \"{sparse_path}\""
    command(cmd)


def convert(result_path, file_type = "TXT"):
    sparse_path = os.path.join(result_path, "sparse")
    lastest_sparse_path = os.path.join(sparse_path, get_latest_folder(sparse_path))

    cmd = f"\"{COLMAP_PATH}\" model_converter " \
              f"--input_path \"{lastest_sparse_path}\" " \
              f"--output_path \"{lastest_sparse_path}\" " \
              f"--output_type {file_type}"
    command(cmd)