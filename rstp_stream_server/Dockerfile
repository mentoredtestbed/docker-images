ARG BASE_REPO=ghcr.io/mentoredtestbed/
ARG BASE_IMAGE=mentored-base
ARG BASE_IMAGE_TAG=latest

# Stage 1: Extract mediamtx binary from official image
FROM bluenviron/mediamtx:1.9.3 AS rtsp

# Intermediate stage to get mentored-base-utils
FROM $BASE_REPO'mentored-base-utils':$BASE_IMAGE_TAG AS utils

# Stage 2: Use mentored-base as final image
FROM $BASE_REPO$BASE_IMAGE:$BASE_IMAGE_TAG

COPY --from=rtsp /mediamtx /
COPY rtsp-simple-server.yml /
COPY ./CREDITS /

# Copy mentored utilities from mentored-base-utils image
COPY --from=utils /entry.sh /
COPY --from=utils /usr/local/bin/* /usr/local/bin/

ENTRYPOINT [ "/mediamtx" ]
