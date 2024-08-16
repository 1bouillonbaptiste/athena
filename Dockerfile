FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04

# install python3
RUN apt-get update \
  && apt-get install -y python3 python3-pip python3-venv \
  && rm -rf /var/lib/apt/lists/*

# install poetry
RUN python3 -m pip install pipx \
    && pipx install --force poetry==1.8.3 \
    && pipx ensurepath
