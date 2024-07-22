FROM debian:bullseye

ENV LANG C.UTF-8

RUN apt-get -qq -y update && \
    apt-get -qq -y install \
    t50 hping3 slowhttptest wondershaper procps python3-pip nano vim curl net-tools iproute2 python3 python3-pip nano

RUN pip3 install --upgrade setuptools
RUN pip3 install --upgrade pip
RUN pip3 install icmplib==3.0.4

COPY ./entry.sh /
COPY ./create_env_from_mentored_ip_list.py /
COPY ./ping_other_ips.py /