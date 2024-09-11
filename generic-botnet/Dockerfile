ARG BASE_REPO=ghcr.io/mentoredtestbed/
ARG BASE_IMAGE=mentored-base
ARG BASE_IMAGE_TAG=latest
FROM $BASE_REPO$BASE_IMAGE:$BASE_IMAGE_TAG

RUN pip3 install slowloris PySocks --break-system-packages

RUN echo "deb http://ftp.de.debian.org/debian bookworm main non-free" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y nikto

COPY mentored-attack /usr/local/bin/