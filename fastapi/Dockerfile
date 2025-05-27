FROM continuumio/miniconda3:latest@sha256:4a2425c3ca891633e5a27280120f3fb6d5960a0f509b7594632cdd5bb8cbaea8

WORKDIR /fastapi

COPY environment.yml .
RUN conda env create -f environment.yml

ENV PATH /opt/conda/envs/fastapi/bin:$PATH

WORKDIR /fastapi/app
