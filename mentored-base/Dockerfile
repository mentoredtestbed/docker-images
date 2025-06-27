FROM debian:bookworm

ENV LANG=C.UTF-8

RUN apt-get -qq -y update && \
    apt-get -qq -y install \
    at \
    curl \
    git \
    iperf3 \
    iproute2 \
    iputils-arping \
    iputils-ping \
    iputils-tracepath \
    less \
    mtr \
    nano \
    net-tools \
    nmap \
    procps \
    python3 \
    python3-icmplib \
    python3-pip \
    python3-psutil \
    python3-setuptools \
    python3-yaml \
    tcpdump \
    vim \
    wondershaper && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


COPY ./entry.sh /
COPY ./create_env_from_mentored_ip_list.py /
COPY ./ping_other_ips.py /

COPY utils/bin/* /usr/local/bin/