FROM debian:trixie-slim

ENV LANG=C.UTF-8

RUN apt -qq -y update && \
    apt -qq -y install --no-install-recommends --no-install-suggests \
    at \
    curl \
    gawk \
    iperf3 \
    iproute2 \
    iputils-arping \
    iputils-ping \
    iputils-tracepath \
    jq \
    kubernetes-client \
    less \
    nano \
    procps \
    python3 \
    python3-icmplib \
    python3-pip \
    python3-psutil \
    python3-setuptools \
    python3-yaml \
    socat \
    tcpdump && \
    apt clean && rm -rf /var/lib/apt/lists/*


COPY ./entry.sh /
COPY ./create_env_from_mentored_ip_list.py /
COPY ./ping_other_ips.py /

COPY utils/bin/* /usr/local/bin/