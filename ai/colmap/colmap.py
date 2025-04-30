import os

import pycolmap

from ..utils import init_dir


def extract_features(colmap_path, frames_path):
    init_dir(colmap_path)
    database_path = os.path.join(colmap_path, "database.db")

    options = pycolmap.ImageReaderOptions()
    options.camera_model = 'PINHOLE'

    pycolmap.extract_features(
        database_path=database_path,
        image_path=frames_path,
        camera_mode=pycolmap.CameraMode.SINGLE,
        camera_model='PINHOLE',
        reader_options=options,
        image_list=[]
    )


def match_sequential(colmap_path, overlap=20):
    database_path = os.path.join(colmap_path, "database.db")

    matching_options = pycolmap.SequentialMatchingOptions()
    matching_options.overlap = overlap

    pycolmap.match_sequential(
        database_path=database_path,
        matching_options=matching_options
    )


def match_exhaustive(colmap_path):
    database_path = os.path.join(colmap_path, "database.db")

    pycolmap.match_exhaustive(database_path)


def incremental_mapping(colmap_path, frames_path):
    sparse_path = os.path.join(colmap_path, "sparse")
    database_path = os.path.join(colmap_path, "database.db")

    reconstructions = pycolmap.incremental_mapping(database_path, frames_path, sparse_path)

    # print(reconstructions)

    for index, reconstruction in reconstructions.items():
        print(index, reconstruction)
        # reconstruction.export_PLY(os.path.join(sparse_path, str(index), "points3D.ply"))
        # reconstruction.write_text(init_dir(os.path.join(sparse_path, str(index), "txt")))