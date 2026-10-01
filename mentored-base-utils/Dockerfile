ARG BASE_REPO=ghcr.io/mentoredtestbed/
ARG BASE_IMAGE=mentored-base
ARG BASE_IMAGE_TAG=latest

FROM $BASE_REPO$BASE_IMAGE:$BASE_IMAGE_TAG

# Copy entry.sh to root
COPY ./entry.sh /

# Copy all binaries and utilities to /usr/local/bin/
COPY ./utils/bin/* /usr/local/bin/