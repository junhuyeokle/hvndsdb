import os

from ai.colmap import extract_features, match_sequential, incremental_mapping
from ai.deblur_gs import train
from ai.utils import extract_frames

EXTRACT_FRAMES = True
EXTRACT_FEATURES = True
MATCH_SEQUENTIAL = True
INCREMENTAL_MAPPING = True
TRAIN = True

# EXTRACT_FRAMES = False
# EXTRACT_FEATURES = True
# MATCH_SEQUENTIAL = True
# INCREMENTAL_MAPPING = True
# TRAIN = True

# EXTRACT_FRAMES = False
# EXTRACT_FEATURES = False
# MATCH_SEQUENTIAL = False
# INCREMENTAL_MAPPING = False
# TRAIN = True


DATA_PATH = "C:\\Devs\\Repos\\ARMap\\data"

building_id = "test-building"
sample_path = os.path.join(DATA_PATH, building_id, "sample.mp4")
deblur_gs_path = os.path.join(DATA_PATH, building_id, "deblur_gs")
colmap_path = os.path.join(DATA_PATH, building_id, "colmap")
frames_path = os.path.join(DATA_PATH, building_id, "frames")

print(sample_path, colmap_path, frames_path, building_id, sep='\n')

if EXTRACT_FRAMES:
    extract_frames(sample_path, frames_path)

if EXTRACT_FEATURES:
    extract_features(colmap_path, frames_path)

if MATCH_SEQUENTIAL:
    match_sequential(colmap_path)

if INCREMENTAL_MAPPING:
    incremental_mapping(colmap_path, frames_path)

if TRAIN:
    train(deblur_gs_path, colmap_path, frames_path)