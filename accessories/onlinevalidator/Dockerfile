FROM python:3.8-slim-buster
# from root pymzqc directory: `podman build -t mzqc-validator -f accessories/onlinevalidator/Dockerfile .`

ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# following line for local testing only (it overrides the latest pymzqc from pypi) 
COPY . /pymzqc/

COPY accessories/onlinevalidator/mzqc_online_validator.py mzqc-validator/
COPY accessories/onlinevalidator/requirements.txt mzqc-validator/
COPY accessories/onlinevalidator/Procfile mzqc-validator/
COPY accessories/onlinevalidator/wsgi.py mzqc-validator/

RUN python -m pip install --upgrade pip
# following line for local testing only (it overrides the latest pymzqc from pypi) 
RUN pip install -e /pymzqc/ 
RUN pip install -r mzqc-validator/requirements.txt 
