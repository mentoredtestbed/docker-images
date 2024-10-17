ARG BASE_REPO=ghcr.io/mentoredtestbed/
ARG BASE_IMAGE=mentored-base
ARG BASE_IMAGE_TAG=latest
FROM ${BASE_REPO}${BASE_IMAGE}:${BASE_IMAGE_TAG}

# Install mosquitto
RUN apt-get update && apt-get install -y mosquitto mosquitto-clients
RUN mkdir /run/mosquitto
RUN chown mosquitto:mosquitto /run/mosquitto
RUN pip install paho-mqtt --break-system-packages

COPY publisher.py /usr/local/bin/publisher.py

CMD ["/usr/sbin/mosquitto", "-v"]