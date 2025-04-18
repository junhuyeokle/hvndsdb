import subprocess

def run_colmap(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(f"Error occurred: {stderr.decode('utf-8')}")
    else:
        print(f"Success: {stdout.decode('utf-8')}")

def extract_features(image_path, database_path):
    command = f"colmap feature_extractor --database_path {database_path} --image_path {image_path}"
    run_colmap(command)
