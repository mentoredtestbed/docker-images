ARG BASE_REPO=ghcr.io/mentoredtestbed/
ARG BASE_IMAGE=mentored-base
ARG BASE_IMAGE_TAG=latest

FROM golang:1.23-bookworm AS gobuilder
RUN apt install -y git
RUN git clone https://github.com/secengjeff/rapidresetclient.git /opt/rapidresetclient
RUN bash -c "pushd /opt/rapidresetclient && go build -o /usr/local/bin/rapidresetclient && popd"

FROM $BASE_REPO$BASE_IMAGE:$BASE_IMAGE_TAG

RUN echo "deb http://ftp.debian.org/debian bookworm main non-free" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y nikto

RUN pip3 install --break-system-packages slowloris PySocks icmplib

COPY --from=gobuilder /usr/local/bin/rapidresetclient /usr/local/bin/rapidresetclient

COPY mentored-attack /usr/local/bin/