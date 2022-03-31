FROM python:3.9-slim-buster
#FROM python:3.6.9-slim-buster
#FROM python:3.6.5-slim-jessie
#FROM python:2.7-slim-jessie
 
ENV DEBIAN_FRONTEND noninteractive 
 
RUN apt-get update && apt-get install -y --no-install-recommends --no-install-suggests \ 
  vim \
  git \
  libgomp1 \
  zlib1g \
  libstdc++6 \
  sudo \
  build-essential \
  libcurl4-openssl-dev

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN echo "deb http://http.debian.net/debian buster main" > /etc/apt/sources.list.d/debian-unstable.list

COPY pymzqc-*-any.whl dist/
RUN python -m pip install --upgrade pip
RUN pip install dist/pymzqc-*-any.whl
