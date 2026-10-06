FROM debian:trixie-slim

ENV LANG=C.UTF-8

RUN apt -qq -y update && \
    apt -qq -y install --no-install-recommends --no-install-suggests \
    argus-client \
    at \
    ca-certificates \
    curl \
    frr \
    frr-pythontools \
    gawk \
    iperf3 \
    iproute2 \
    iputils-arping \
    iputils-ping \
    iputils-tracepath \
    jq \
    kubernetes-client \
    ldnsutils \
    less \
    nano \
    net-tools \
    procps \
    python3 \
    python3-icmplib \
    python3-pip \
    python3-psutil \
    python3-setuptools \
    python3-yaml \
    socat \
    tcpdump \
    tshark \
    ulogd2 \
    unzip \
    vim \
    wget \
    && \
    apt clean && rm -rf /var/lib/apt/lists/*