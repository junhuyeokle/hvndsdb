import os

import pycolmap

from .configs import COLMAP_EXE_PATH
from .utils import set_dir, command, get_latest_folder


def reconstruct(colmap_path, frames_path):
    reconstruction = pycolmap.incremental_mapping(
        database_path=os.path.join(colmap_path, "database.db"),
        image_path=frames_path,
        output_path=os.path.join(colmap_path, "sparse"),
    )
    return reconstruction


def extract(colmap_path, frames_path):
    set_dir(colmap_path)
    database_path = os.path.join(colmap_path, "database.db")

    cmd = f"\"{COLMAP_EXE_PATH}\" feature_extractor " \
          f"--database_path \"{database_path}\" " \
          f"--image_path \"{frames_path}\""
    command(cmd)


def match(colmap_path):
    database_path = os.path.join(colmap_path, "database.db")

    cmd = f"\"{COLMAP_EXE_PATH}\" exhaustive_matcher " \
          f"--database_path \"{database_path}\""
    command(cmd)


def pair(colmap_path, frames_path):
    sparse_path = set_dir(os.path.join(colmap_path, "sparse"))
    database_path = os.path.join(colmap_path, "database.db")

    cmd = f"\"{COLMAP_EXE_PATH}\" mapper " \
          f"--database_path \"{database_path}\" " \
          f"--image_path \"{frames_path}\" " \
          f"--output_path \"{sparse_path}\""
    command(cmd)


def convert(colmap_path, from_type ="BIN", to_type="TXT"):
    sparse_path = os.path.join(colmap_path, "sparse")
    lastest_sparse_path = os.path.join(sparse_path, get_latest_folder(sparse_path))
    input_path = lastest_sparse_path if from_type == "BIN" else os.path.join(lastest_sparse_path, from_type.lower())
    output_path = set_dir(os.path.join(lastest_sparse_path, to_type.lower())) if to_type != "PLY" else os.path.join(lastest_sparse_path, to_type.lower(), "points3D.ply")

    cmd = f"\"{COLMAP_EXE_PATH}\" model_converter " \
          f"--input_path \"{input_path}\" " \
          f"--output_path \"{output_path}\" " \
          f"--output_type {to_type}"
    command(cmd)