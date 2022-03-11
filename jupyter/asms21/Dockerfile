FROM python:3.9-slim-buster
#FROM python:3.6.9-slim-buster
#FROM python:3.6.5-slim-jessie
#FROM python:2.7-slim-jessie
 
ENV DEBIAN_FRONTEND noninteractive 
COPY asms21-pylib_demo.complete.ipynb /asms21-pylib_demo.complete.ipynb
COPY CPTAC_CompRef_00_iTRAQ_01_2Feb12_Cougar_11-10-09_ids.csv /CPTAC_CompRef_00_iTRAQ_01_2Feb12_Cougar_11-10-09_ids.csv
COPY CPTAC_CompRef_00_iTRAQ_01_2Feb12_Cougar_11-10-09.mzQC /CPTAC_CompRef_00_iTRAQ_01_2Feb12_Cougar_11-10-09.mzQC

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

RUN pip install pandas numpy scipy pronto jupyter requests plotly kaleido
RUN pip install -U git+https://github.com/MS-Quality-hub/pymzqc.git@v1.0.0#egg=pymzqc
