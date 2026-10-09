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

ENV DEBIAN_FRONTEND=noninteractive

# Install additional packages not in mentored-base
RUN echo "deb http://ftp.debian.org/debian bookworm main non-free" > /etc/apt/sources.list.d/bookworm-non-free.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    hping3 \
    hydra \
    nikto \
    nmap \
    rsyslog \
    openssh-server \
    ssh \
    sshpass \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages distlib psutil pyaml==24.7.0 icmplib slowloris PySocks

# Copy rapidresetclient from builder
COPY --from=gobuilder /usr/local/bin/rapidresetclient /usr/local/bin/rapidresetclient

WORKDIR /app

COPY ./attacker.sh /app
COPY ./vulnerable.sh /app
COPY ./start_sshd.sh /app
COPY ./10000_common_passwords /app
COPY ./10_common_passwords /app
COPY ./attacker.py /app
RUN chmod +x /app/*.sh

RUN echo "auth.* /app/results/sshd.log" > /etc/rsyslog.d/50-sshd.conf

# Copy mentored utilities from mentored-base-utils image
COPY --from=utils /entry.sh /
COPY --from=utils /usr/local/bin/* /usr/local/bin/

#ENTRYPOINT ["tcpdump", "-i", "eth0", "-w", "pcap_server.pcap"]
