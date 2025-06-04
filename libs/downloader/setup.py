from setuptools import setup, find_packages

setup(
    name="downloader",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
    ],
    python_requires=">=3.7",
    author="DPChanny",
    description="Async utility for uploading/downloading folders via presigned URLs.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
