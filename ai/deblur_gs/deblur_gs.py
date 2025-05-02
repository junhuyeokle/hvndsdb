from .configs import DEBLUR_GS_TRAIN_PATH, DEBLUR_GS_PYTHON_PATH
from ..utils import command, init_dir


def deblur_gs(cmd):
    command(f'powershell -Command "conda activate deblur_gs; {cmd}"')


def train(deblur_gs_path, colmap_path, frames_path):
    deblur_gs_path = init_dir(deblur_gs_path)

    iteration = 10000
    save_interval = 500
    checkpoint_interval = 1000

    cmd = (
        f'{DEBLUR_GS_PYTHON_PATH} "{DEBLUR_GS_TRAIN_PATH}" '
        f'-s "{colmap_path}" '
        f'-m "{deblur_gs_path}" '
        f'-i "{frames_path}" '
        f"--iterations {iteration} "
        f"--test_iterations -1 "
        f"--save_iterations {" ".join([str(i) for i in range(0, iteration + 1, save_interval)])} "
        f"--checkpoint_iterations {" ".join([str(i) for i in range(0, iteration + 1, checkpoint_interval)])} "
        f"--deblur"
    )

    print(cmd)
