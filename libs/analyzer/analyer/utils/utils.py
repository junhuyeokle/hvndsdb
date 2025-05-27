import os
import shutil
import cv2


def extract_frames(sample_path, frames_path, frames_per_second=5, width=600, height=400):
    cap = cv2.VideoCapture(sample_path)
    frames_path = init_dir(frames_path)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    source_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_interval = max(int(source_fps // frames_per_second), 1)

    num_digits = len(str(total_frames))
    read_frame_count = 0
    saved_frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if read_frame_count % frame_interval == 0:
            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
            filename = os.path.join(frames_path, f"{saved_frame_count:0{num_digits}d}.png")
            cv2.imwrite(filename, frame)
            saved_frame_count += 1

        read_frame_count += 1

    cap.release()


def init_dir(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
    return path


def get_latest_folder(directory):
    folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]

    latest_folder = max(folders, key=lambda x: int(x) if x.isdigit() else -1)
    return latest_folder
