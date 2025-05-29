FROM continuumio/miniconda3:latest@sha256:4a2425c3ca891633e5a27280120f3fb6d5960a0f509b7594632cdd5bb8cbaea8

RUN apt-get update && apt-get install -y libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

WORKDIR /libs
COPY ./libs ./

WORKDIR /fastapi

COPY ./fastapi/environment.yml ./
RUN conda env create -f environment.yml && conda clean -afy

ENV PATH=/opt/conda/envs/fastapi/bin:$PATH

WORKDIR /fastapi/app
