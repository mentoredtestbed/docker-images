ARG BASE_REPO=ghcr.io/mentoredtestbed/
ARG BASE_IMAGE=mentored-base
ARG BASE_IMAGE_TAG=latest

# Intermediate stage to get mentored-base-utils
FROM $BASE_REPO'mentored-base-utils':$BASE_IMAGE_TAG AS utils

# Main image
FROM $BASE_REPO$BASE_IMAGE:$BASE_IMAGE_TAG

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-netifaces python3-numpy python3-httpx && \
    pip3 install --break-system-packages httpx[http2] && \
    rm -rf /var/lib/apt/lists/*

COPY ./client_web_metrics.py /

COPY ./bin/* /usr/local/bin/

# Copy mentored utilities from mentored-base-utils image
COPY --from=utils /entry.sh /
COPY --from=utils /usr/local/bin/* /usr/local/bin/
