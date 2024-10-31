ARG BASE_REPO=ghcr.io/mentoredtestbed/
ARG BASE_IMAGE=mentored-base
ARG BASE_IMAGE_TAG=latest
FROM $BASE_REPO$BASE_IMAGE:$BASE_IMAGE_TAG

RUN apt update && apt install -y --no-install-recommends \
    iputils-ping \
    python3 \
    ffmpeg \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# To make this device vulnerable to Mirai, we need a telnet server and the busybox shell.
# busybox from Debian repos does not include 'telnetd'.
# By default, this does not make it vulnerable because telnetd is not running automatically.
# RUN wget https://busybox.net/downloads/binaries/1.35.0-x86_64-linux-musl/busybox &&\
#     chmod +x busybox &&\
#     mv busybox /bin &&\
#     printf '#!/bin/sh\n/bin/busybox sh\n' > /bin/busyboxsh &&\
#     chmod +x /bin/busyboxsh

COPY street_london_rainy_night-720p-15fps-noaudio.mp4 /video.mp4
COPY ip_camera.py /ip_camera.py
COPY ./CREDITS /
RUN chmod +x /ip_camera.py

# ffmpeg
# -an      : remove audio
# -r       : set frame rate in fps
# -s:v     : set video frame size wxh
# -codec:v : video format

# This is very slow to generate in buildx for AAarch64, so I've disabled it
# RUN ffmpeg -i /original.mp4 -an -r 15 -s:v 1280x720 -codec:v libx265 /video.mp4 &&\
#     rm -f /original.mp4 &&\
#     ffprobe /video.mp4 &&\
#     ls -lh /video.mp4

# ENTRYPOINT [ "/ip_camera.py" ]