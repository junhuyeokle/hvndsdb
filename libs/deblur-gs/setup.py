from setuptools import setup, find_packages

setup(
    name="deblur_gs",
    version="0.1.0",
    description="Deblur Gaussian Splatting",
    author="Wenbo Chen",
    author_email="chaphlagical@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "opencv-python",
        "easydict",
        "tqdm",
        "timm",
        "tensorboard",
        "torchmetrics",
        "scipy",
        "matplotlib",
        "visdom",
    ],
    python_requires=">=3.7,<3.8",
)
