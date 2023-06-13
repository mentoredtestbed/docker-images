FROM ubuntu
ENV LANG C.UTF-8
RUN apt -y update && \
apt -y install \
wondershaper procps python3 python3-pip nano vim net-tools iproute2 wget iputils* curl unzip argus-client
RUN echo "wireshark-common wireshark-common/install-setuid boolean true" | debconf-set-selections
WORKDIR ./app
COPY ./entry.sh /app
