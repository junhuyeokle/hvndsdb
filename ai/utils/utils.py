import subprocess
import threading
import collections
import sys
import time
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


def command(cmd, n=10, sleep_time=0.0):
    print(f"CMD: {cmd}")

    is_tty = sys.stdout.isatty()

    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True,
        encoding="utf-8",
    )

    def stream_output(_stream, _name):
        if is_tty:
            lines = collections.deque(maxlen=n)
            total_lines = 0

            try:
                for line in iter(_stream.readline, ""):
                    formatted = f"[{_name}] {line.rstrip()}"
                    lines.append(formatted)
                    total_lines += 1

                    if total_lines <= n:
                        print(formatted)
                    else:
                        sys.stdout.write(f"\033[{n}F")
                        for l in lines:
                            sys.stdout.write("\033[K")
                            print(l)
                        sys.stdout.write(f"\033[{n}E")
                        sys.stdout.flush()

                    if sleep_time > 0.0:
                        time.sleep(sleep_time)
            finally:
                _stream.close()
        else:
            try:
                for line in iter(_stream.readline, ""):
                    formatted = f"[{_name}] {line.rstrip()}"
                    print(formatted)
                    if sleep_time > 0.0:
                        time.sleep(sleep_time)
            finally:
                _stream.close()

    threads = []
    for stream, name in [(process.stdout, "STDOUT"), (process.stderr, "STDERR")]:
        t = threading.Thread(target=stream_output, args=(stream, name))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    process.wait()

    if process.returncode != 0:
        print(f"ERROR: process exited with code {process.returncode}")
    else:
        print("SUCCESS")
