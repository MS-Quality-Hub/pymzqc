FROM python:3.8-slim-buster
#FROM python:3.6.9-slim-buster
 
ENV DEBIAN_FRONTEND noninteractive 
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

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# # only packages related to dev, project dependencies will get resolved via pip and setup.py
RUN python3 -m pip install --upgrade pip 
RUN pip install matplotlib pytest mypy types-setuptools sphinx build wheel twine click flask flask_restful flask_cors

#RUN pip install -e .  # devcontainer.json: "postCreateCommand": "pip install -e .",

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME 
RUN echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME
RUN echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME
    
#USER 1000  # "runArgs": ["-u", "1000"]
#extrawurst fuer vscode
#RUN mkdir -p /root