FROM python:3.8-slim-buster

ENV DEBIAN_FRONTEND noninteractive 
 
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

COPY mzqc_online_validator.py mzqc-validator/
COPY requirements.txt mzqc-validator/
COPY Procfile mzqc-validator/

RUN python -m pip install --upgrade pip
RUN pip install -r mzqc-validator/requirements.txt 
