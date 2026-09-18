FROM python:3.8-slim-buster
# From the pymzqc repository root, first build/copy a wheel into the build
# context, then run:
#   podman build -t mzqc-validator -f mzqcaccessories/onlinevalidator/Dockerfile .

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Release workflows download the already-built pymzqc wheel into the repository
# root. Installing that artifact avoids requiring .git metadata inside Docker for
# hatch-vcs version discovery and guarantees the validator uses the exact wheel
# produced by the release build.
COPY pymzqc-*-any.whl /tmp/

COPY mzqcaccessories/onlinevalidator/mzqc_online_validator.py mzqc-validator/
COPY mzqcaccessories/onlinevalidator/requirements.txt mzqc-validator/
COPY mzqcaccessories/onlinevalidator/Procfile mzqc-validator/

RUN python -m pip install --upgrade pip
RUN pip install /tmp/pymzqc-*-any.whl
RUN pip install -r mzqc-validator/requirements.txt
