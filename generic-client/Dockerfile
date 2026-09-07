ARG BASE_REPO=ghcr.io/mentoredtestbed/
ARG BASE_IMAGE=mentored-base
ARG BASE_IMAGE_TAG=latest
FROM $BASE_REPO$BASE_IMAGE:$BASE_IMAGE_TAG

RUN apt -qq -y update && \
    apt -qq -y install --no-install-recommends --no-install-suggests \
    python3-httpx \
    python3-netifaces \
    python3-numpy \
    && apt clean && rm -rf /var/lib/apt/lists/* 
# RUN pip3 install --break-system-packages numpy httpx[http2] netifaces

COPY ./client_web_metrics.py /

COPY ./bin/* /usr/local/bin/
