from os import path
from colmap.commands import extract_camera_poses
from colmap.configs import DATA_PATH

building_id = "test-building"
colmap_path = path.join(DATA_PATH, building_id, "colmap")
frames_path = path.join(DATA_PATH, building_id, "frames")

print(colmap_path, frames_path, building_id, sep='\n')
#
# extract_features(frames_path, result_path)
#
# image_matching(result_path)
#
# mapper(frames_path, result_path)

# extract_3d_points_and_6dof(result_path)

camera_poses = extract_camera_poses(colmap_path)

# 카메라 포즈 출력
for image_name, pose in camera_poses.items():
    print(f"Image {image_name}: Position = {pose['position']}, Rotation = {pose['rotation']}")