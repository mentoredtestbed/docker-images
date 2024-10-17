ARG BASE_REPO=ghcr.io/mentoredtestbed/
ARG BASE_IMAGE=mentored-base
ARG BASE_IMAGE_TAG=latest
FROM ${BASE_REPO}${BASE_IMAGE}:${BASE_IMAGE_TAG}

# Install mosquitto
RUN apt-get update && apt-get install -y mosquitto mosquitto-clients
RUN mkdir /run/mosquitto
RUN chown mosquitto:mosquitto /run/mosquitto
RUN pip install paho-mqtt --break-system-packages

COPY client.py /usr/local/bin/client.py

# Create drop-in config files to log to stdout, listen on 0.0.0.0 and store data in /app/mqtt-broker
RUN mkdir -p /etc/mosquitto/conf.d
RUN echo "log_dest stdout" > /etc/mosquitto/conf.d/01-stdout.conf
RUN echo "allow_anonymous true" > /etc/mosquitto/conf.d/02-allow-anonymous.conf
RUN echo "listener 1883" > /etc/mosquitto/conf.d/02-listener.conf
RUN echo "persistence true" > /etc/mosquitto/conf.d/03-persistence.conf
RUN mkdir -p /app/mqtt-broker
RUN echo "persistence_location /app/mqtt-broker/" > /etc/mosquitto/conf.d/04-persistence-location.conf
RUN echo "include_dir /etc/mosquitto/conf.d" > /etc/mosquitto/mosquitto.conf

CMD ["/usr/sbin/mosquitto", "-c", "/etc/mosquitto/mosquitto.conf", "-v"]