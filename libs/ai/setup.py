from setuptools import setup, find_packages

setup(
    name="ai",
    version="0.1.0",
    description="AI",
    author="DPChanny",
    author_email="kyoungchan0516@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "opencv-python",
        "pycolmap"
    ],
    python_requires=">=3.12"
)
