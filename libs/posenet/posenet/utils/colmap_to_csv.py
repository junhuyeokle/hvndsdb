import os
import csv

def parse_images_txt(images_txt_path):
    entries = []
    with open(images_txt_path, 'r') as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#') or line == '':
            i += 1
            continue
        vals = line.split()
        if len(vals) >= 10:
            image_id, qw, qx, qy, qz, tx, ty, tz, camera_id, image_name = vals[:10]
            image_name = os.path.basename(image_name)
            entries.append([
                image_name,
                float(tx), float(ty), float(tz),
                float(qx), float(qy), float(qz), float(qw)
            ])
            i += 2
        else:
            i += 1
    return entries

def write_csv(entries, output_csv_path, image_dir):
    with open(output_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['image_path', 'tx', 'ty', 'tz', 'qx', 'qy', 'qz', 'qw'])
        for row in entries:
            full_path = os.path.join(image_dir, row[0])
            writer.writerow([full_path] + row[1:])
