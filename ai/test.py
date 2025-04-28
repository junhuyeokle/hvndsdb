from os import path

from colmap import extract, match, pair, convert, reconstruct
from deblur_gs import train

DATA_PATH = "C:\\Devs\\Repos\\ARMap\\data"

building_id = "test-building"
colmap_path = path.join(DATA_PATH, building_id, "colmap")
frames_path = path.join(DATA_PATH, building_id, "frames")

print(colmap_path, frames_path, building_id, sep='\n')

init = False

if init:
    extract(frames_path, colmap_path)
    match(colmap_path)

    pair(frames_path, colmap_path)

convert(colmap_path, "TXT")
# convert(colmap_path, "PLY")

print(reconstruct(colmap_path, frames_path))

# train(colmap_path)