FROM python:3.8-slim-buster
 
ENV DEBIAN_FRONTEND noninteractive 
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Replace sources with HTTPS sources and add unstable 
RUN printf "deb https://deb.debian.org/debian buster main\ndeb https://security.debian.org/debian-security buster/updates main\ndeb https://ftp.debian.org/debian buster-updates main\n" > /etc/apt/sources.list
#RUN printf "deb https://deb.debian.org/debian unstable main\n" >> /etc/apt/sources.list

COPY pymzqc-*-any.whl dist/
RUN python -m pip install --upgrade pip
RUN pip install dist/pymzqc-*-any.whl