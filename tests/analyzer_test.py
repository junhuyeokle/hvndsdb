import os

from analyzer.colmap import (
    extract_features,
    match_sequential,
    incremental_mapping,
    match_exhaustive,
    match_hybrid,
)
from analyzer.utils import extract_frames


class Config:
    DATA_PATH = "C:\\Devs\\Repos\\HVNDSDB\\data"

    def __init__(
        self,
        building_id,
        EXTRACT_FRAMES=True,
        EXTRACT_FEATURES=True,
        MATCH_HYBRID=False,
        MATCH_SEQUENTIAL=True,
        MATCH_EXHAUSTIVE=False,
        INCREMENTAL_MAPPING=True,
        TRAIN=True,
    ):
        self.sample_path = os.path.join(
            Config.DATA_PATH, building_id, "sample.mp4"
        )
        self.deblur_gs_path = os.path.join(
            Config.DATA_PATH, building_id, "deblur_gs"
        )
        self.colmap_path = os.path.join(Config.DATA_PATH, building_id, "colmap")
        self.frames_path = os.path.join(Config.DATA_PATH, building_id, "frames")

        self.EXTRACT_FRAMES = EXTRACT_FRAMES
        self.EXTRACT_FEATURES = EXTRACT_FEATURES
        self.MATCH_HYBRID = MATCH_HYBRID
        self.MATCH_SEQUENTIAL = MATCH_SEQUENTIAL
        self.MATCH_EXHAUSTIVE = MATCH_EXHAUSTIVE
        self.INCREMENTAL_MAPPING = INCREMENTAL_MAPPING
        self.TRAIN = TRAIN

        self.MATCH_SEQUENTIAL = (
            False if self.MATCH_HYBRID else self.MATCH_SEQUENTIAL
        )
        self.MATCH_EXHAUSTIVE = (
            False if self.MATCH_HYBRID else self.MATCH_EXHAUSTIVE
        )


building_id = "test-building-1"

config = Config(building_id)

print(
    config.sample_path,
    config.colmap_path,
    config.frames_path,
    building_id,
    sep="\n",
)

if config.EXTRACT_FRAMES:
    extract_frames(config.sample_path, config.frames_path)

if config.EXTRACT_FEATURES:
    extract_features(config.colmap_path, config.frames_path)

if config.MATCH_SEQUENTIAL:
    match_sequential(config.colmap_path, overlap=500)

if config.MATCH_EXHAUSTIVE:
    match_exhaustive(config.colmap_path)

if config.MATCH_HYBRID:
    match_hybrid(config.colmap_path)

if config.INCREMENTAL_MAPPING:
    incremental_mapping(config.colmap_path, config.frames_path)
