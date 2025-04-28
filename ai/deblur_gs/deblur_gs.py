from .configs import DEBLUR_GS_PATH
from .utils import command


def deblur_gs(cmd):
    command("SET DISTUTILS_USE_SDK=1\n" + "conda activate deblur_gs\n" + cmd + "\n" + "conda deactivate")


def train(result_path):
    cmd = f"python \"{DEBLUR_GS_PATH}\\train.py\" -s \"{result_path}\" --eval --deblur"

    deblur_gs(cmd)
