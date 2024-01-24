FROM python:3.8-slim-buster
# Alt.:
# https://mcr.microsoft.com/en-us/product/devcontainers/python/about

# ********************************************************
# * setup for debian based
#   (also see container/DevDockerfile)
# ********************************************************

ENV DEBIAN_FRONTEND noninteractive 
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Replace sources with HTTPS sources and add unstable 
RUN printf "deb https://deb.debian.org/debian buster main\ndeb https://security.debian.org/debian-security buster/updates main\ndeb https://ftp.debian.org/debian buster-updates main\n" > /etc/apt/sources.list
#RUN printf "deb https://deb.debian.org/debian unstable main\n" >> /etc/apt/sources.list
 
RUN apt-get update && apt-get install -y --no-install-recommends --no-install-suggests \ 
  git \
  vim \
  libqt4-network \
  libgomp1 \
  zlib1g \
  libstdc++6 \
  sudo \
  build-essential \
  libcurl4-openssl-dev \
  ssh-client\
  graphviz

# # only packages related to dev, project dependencies will get resolved via pip and setup.py
RUN python3 -m pip install --upgrade pip 
RUN pip install pytest mypy types-setuptools sphinx build wheel twine \
    jsonschema strict-rfc3339 rfc3339-validator \
    requests flask flask_restful flask_cors \ 
    matplotlib hvplot panel jupyter plotly kaleido numpy pandas scipy \
    lxml pyteomics click

# ********************************************************
# * extrawurst fuer vscode
# ********************************************************

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /bin/bash \
    #
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# ********************************************************
# * Anything else you want to do like clean up goes here 
# ********************************************************

# [Optional] Set the default user. Omit if you want to keep the default as root.
USER $USERNAME:$USERNAME