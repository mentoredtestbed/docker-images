FROM ghcr.io/mentoredtestbed/mentored-base:latest

RUN echo "deb http://ftp.de.debian.org/debian bookworm main non-free" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y nikto

RUN pip3 install --break-system-packages slowloris PySocks icmplib

COPY mentored-attack /usr/local/bin/