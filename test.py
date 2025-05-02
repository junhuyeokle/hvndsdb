import os

from ai.colmap import (
    extract_features,
    match_sequential,
    incremental_mapping,
    match_exhaustive,
    match_hybrid,
)
from ai.deblur_gs import train
from ai.utils import extract_frames

EXTRACT_FRAMES = True
EXTRACT_FEATURES = True
MATCH_HYBRID = False
MATCH_SEQUENTIAL = True
MATCH_EXHAUSTIVE = False
INCREMENTAL_MAPPING = True
TRAIN = True

# DO NOT CHANGE FROM BOTTOM OF THIS LINE

MATCH_SEQUENTIAL = False if MATCH_HYBRID else MATCH_SEQUENTIAL
MATCH_EXHAUSTIVE = False if MATCH_HYBRID else MATCH_EXHAUSTIVE

DATA_PATH = "C:\\Devs\\Repos\\HVNDSDB\\data"

building_id = "test-building-1"
sample_path = os.path.join(DATA_PATH, building_id, "sample.mp4")
deblur_gs_path = os.path.join(DATA_PATH, building_id, "deblur_gs")
colmap_path = os.path.join(DATA_PATH, building_id, "colmap")
frames_path = os.path.join(DATA_PATH, building_id, "frames")

print(sample_path, colmap_path, frames_path, building_id, sep="\n")

if EXTRACT_FRAMES:
    extract_frames(sample_path, frames_path)

if EXTRACT_FEATURES:
    extract_features(colmap_path, frames_path)

if MATCH_SEQUENTIAL:
    match_sequential(colmap_path)

if MATCH_EXHAUSTIVE:
    match_exhaustive(colmap_path)

if MATCH_HYBRID:
    match_hybrid(colmap_path)

if INCREMENTAL_MAPPING:
    incremental_mapping(colmap_path, frames_path)

if TRAIN:
    train(deblur_gs_path, colmap_path, frames_path)
