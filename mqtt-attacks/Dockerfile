ARG BASE_REPO=ghcr.io/mentoredtestbed/
ARG BASE_IMAGE_TAG=latest
FROM ${BASE_REPO}"infection-scenario":${BASE_IMAGE_TAG}

# Install mosquitto
RUN apt-get update && apt install -y tshark
RUN git clone https://github.com/stfbk/mqttsa.git /usr/local/bin/mqttsa &&\
    cd /usr/local/bin/mqttsa &&\
    pip install -r requirements.txt --break-system-packages

# Increase the number of file descriptors, needed for more connections
RUN ulimit -n 65535

# Yes, this is needed otherwise the final report will not be printed
WORKDIR /usr/local/bin/mqttsa


CMD ["python3", "mqttsa.py", "localhost"]