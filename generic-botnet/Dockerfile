ARG BASE_REPO=ghcr.io/mentoredtestbed/
ARG BASE_IMAGE=mentored-base
ARG BASE_IMAGE_TAG=latest

# Build stage for rapidresetclient
FROM golang:1.23-bookworm AS gobuilder
RUN apt install -y git
RUN git clone https://github.com/secengjeff/rapidresetclient.git /opt/rapidresetclient
RUN bash -c "pushd /opt/rapidresetclient && go build -o /usr/local/bin/rapidresetclient && popd"

# Intermediate stage to get mentored-base-utils
FROM $BASE_REPO'mentored-base-utils':$BASE_IMAGE_TAG AS utils

# Main image
FROM $BASE_REPO$BASE_IMAGE:$BASE_IMAGE_TAG

# Install additional packages not in mentored-base
RUN echo "deb http://ftp.debian.org/debian bookworm main non-free" > /etc/apt/sources.list.d/bookworm-non-free.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    hping3 \
    nikto \
    nmap \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages slowloris PySocks icmplib

# Copy rapidresetclient from builder
COPY --from=gobuilder /usr/local/bin/rapidresetclient /usr/local/bin/rapidresetclient

# Copy mentored utilities from mentored-base-utils image (includes mentored-attack)
COPY --from=utils /entry.sh /
COPY --from=utils /usr/local/bin/* /usr/local/bin/

# Copy botnet attack scripts
COPY botnet_orchestrator.sh /app/botnet_orchestrator.sh
COPY hping3_attack.sh /app/hping3_attack.sh
RUN chmod +x /app/*.sh