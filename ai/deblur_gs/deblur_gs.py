from .configs import DEBLUR_GS_TRAIN_PATH, DEBLUR_GS_PYTHON_PATH
from ..utils import command, init_dir


def deblur_gs(cmd):
    command(f'powershell -Command "conda activate deblur_gs; {cmd}"')


def train(deblur_gs_path, colmap_path, frames_path):
    deblur_gs_path = init_dir(deblur_gs_path)

    cmd = f"{DEBLUR_GS_PYTHON_PATH} \"{DEBLUR_GS_TRAIN_PATH}\" " \
          f"-s \"{colmap_path}\" " \
          f"-m \"{deblur_gs_path}\" " \
          f"-i \"{frames_path}\" " \
          f"--deblur"

    print(cmd)
