import subprocess
import threading
import collections
import sys
import time
import os
import shutil

def set_dir(path):
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

    process = subprocess.Popen(
        cmd, shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True
    )

    def stream_output(_stream, _name):
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
