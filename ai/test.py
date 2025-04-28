from os import path

from colmap import extract, match, pair, convert
from deblur_gs import train

DATA_PATH = "C:\\Devs\\Repos\\ARMap\\data"

building_id = "test-building"
deblur_gs_path = path.join(DATA_PATH, building_id, "deblur_gs")
colmap_path = path.join(DATA_PATH, building_id, "colmap")
frames_path = path.join(DATA_PATH, building_id, "frames")

print(colmap_path, frames_path, building_id, sep='\n')

init = False

if init:
    extract(colmap_path, frames_path)
    match(colmap_path)

    pair(colmap_path, frames_path)

convert(colmap_path)
convert(colmap_path, from_type="TXT", to_type="PLY")

train(deblur_gs_path, colmap_path, frames_path)