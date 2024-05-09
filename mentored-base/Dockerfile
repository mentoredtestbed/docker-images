FROM debian

ENV LANG C.UTF-8

RUN apt-get -qq -y update && \
    apt-get -qq -y install \
    t50 hping3 slowhttptest wondershaper procps python3-pip nano vim curl net-tools iproute2
   
COPY ./entry.sh /
COPY ./create_env_from_mentored_ip_list.py /