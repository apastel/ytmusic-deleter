FROM mcr.microsoft.com/devcontainers/base:jammy

# Pre-install GUI/X11 deps (cached layer)
USER root
RUN apt-get update && apt-get install -y \
    libdbus-1-3 libxcb-cursor0 libxcb-xinerama0 libxcb-icccm4 \
    libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxkbcommon-x11-0 \
    libfontconfig1 libfreetype6 libgl1 libegl1-mesa libglvnd-dev libxcb-shape0 \
    && ldconfig \
    && rm -rf /var/lib/apt/lists/*

USER vscode
