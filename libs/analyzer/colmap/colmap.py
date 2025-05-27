import os

import pycolmap

from ..utils import init_dir


def extract_features(colmap_path, frames_path):
    init_dir(colmap_path)
    database_path = os.path.join(colmap_path, "database.db")

    options = pycolmap.ImageReaderOptions()
    options.camera_model = "SIMPLE_PINHOLE"

    pycolmap.extract_features(
        device=pycolmap.Device.auto,
        database_path=database_path,
        image_path=frames_path,
        camera_mode=pycolmap.CameraMode.SINGLE,
        camera_model="SIMPLE_PINHOLE",
        reader_options=options,
        image_list=[],
    )


def match_sequential(colmap_path, overlap=10, device=pycolmap.Device.auto):
    database_path = os.path.join(colmap_path, "database.db")

    matching_options = pycolmap.SequentialMatchingOptions()
    matching_options.overlap = overlap

    pycolmap.match_sequential(
        database_path=database_path,
        matching_options=matching_options,
        device=device,
    )


def match_exhaustive(colmap_path, block_size=100, device=pycolmap.Device.auto):
    database_path = os.path.join(colmap_path, "database.db")

    matching_options = pycolmap.ExhaustiveMatchingOptions()
    matching_options.block_size = block_size

    try:
        pycolmap.match_exhaustive(
            database_path=database_path,
            matching_options=matching_options,
            device=device,
        )
    except Exception as e:
        print(f"{e}")


def match_hybrid(
    colmap_path, overlap=10, block_size=100, device=pycolmap.Device.auto
):
    match_sequential(colmap_path, overlap)
    match_exhaustive(colmap_path, block_size, device)


def incremental_mapping(colmap_path, frames_path):
    sparse_path = init_dir(os.path.join(colmap_path, "sparse"))
    database_path = os.path.join(colmap_path, "database.db")

    reconstructions = pycolmap.incremental_mapping(
        database_path=database_path,
        image_path=frames_path,
        output_path=sparse_path,
    )

    for index, reconstruction in reconstructions.items():
        reconstruction.write_text(
            init_dir(os.path.join(sparse_path, str(index), "txts"))
        )
        print(index, reconstruction)
