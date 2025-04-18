from os import path
from colmap import extract_features

data_path = "D:\\P\\Packaged Projects\\ARMap Project\\ARMap\\data"
colmap_path = "D:\\P\\Packaged Projects\\ARMap Project\\ARMap\\colmap\\bin\\colmap.exe"
building_id = "test-building"
result_path = path.join(data_path, building_id, "colmap")
frames_path = path.join(data_path, building_id, "frames")

print(result_path, frames_path, colmap_path, building_id, sep='\n')

extract_features(colmap_path, frames_path, result_path)