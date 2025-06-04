import os
from .colmap_to_csv import parse_images_txt, write_csv

def convert_colmap_to_csv(colmap_root, frames_root):
    images_txt = None

    for root, dirs, files in os.walk(colmap_root):
        for file in files:
            if file == 'images.txt':
                images_txt = os.path.join(root, file)
                break
        if images_txt:
            break

    if not images_txt:
        raise FileNotFoundError("❌ Could not find 'images.txt' in Colmap structure.")

    if not os.path.exists(frames_root):
        raise FileNotFoundError(f"❌ Could not find frames folder at {frames_root}")

    output_csv = os.path.join(colmap_root, 'poses.csv')
    entries = parse_images_txt(images_txt)
    write_csv(entries, output_csv, frames_root)
    print(f"✅ Colmap data processed to CSV: {output_csv}")
    return output_csv
