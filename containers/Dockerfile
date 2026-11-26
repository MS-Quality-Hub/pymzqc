FROM python:3.13-slim
 
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

COPY pymzqc-*-any.whl dist/
RUN python -m pip install --upgrade pip
RUN pip install dist/pymzqc-*-any.whl