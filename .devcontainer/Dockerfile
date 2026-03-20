FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    git \
    binutils \
    libglib2.0-0 \
    libdbus-1-3 \
    libxcb-cursor0 libxcb-xinerama0 libxcb-icccm4 \
    libxcb-image0 libxcb-keysyms1 libxcb-render-util0 \
    libxkbcommon-x11-0 \
    libfontconfig1 libfreetype6 \
    libgl1 libegl1 libglvnd-dev \
    libxcb-shape0 \
    libxrender1 libxext6 libsm6 \
    && rm -rf /var/lib/apt/lists/*

# Create vscode user (matches devcontainer expectations)
RUN useradd -ms /bin/bash vscode
USER vscode
