from os import path

from colmap import DATA_PATH, parse_images, parse_points

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

# converter(colmap_path)

images = parse_images(colmap_path)

for image_name, pose in images.items():
    print(f"Image {image_name}: Position = {pose['position']}, Rotation = {pose['rotation']}")

points = parse_points(colmap_path)

for point in points:
    print(f"Point: {point}")
