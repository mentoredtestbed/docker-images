FROM ghcr.io/mentoredtestbed/mentored-base:latest

RUN pip3 install slowloris PySocks --break-system-packages

RUN echo "deb http://ftp.de.debian.org/debian bookworm main non-free" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y nikto

COPY mentored-attack /usr/local/bin/