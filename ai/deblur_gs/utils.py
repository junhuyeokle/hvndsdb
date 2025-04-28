import subprocess


def command(cmd):
    print(f"CMD: {cmd}")

    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(f"ERROR: {stderr.decode('utf-8')}")
    else:
        print(f"SUCCESS: {stdout.decode('utf-8')}")