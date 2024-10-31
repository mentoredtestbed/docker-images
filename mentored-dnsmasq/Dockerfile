ARG BASE_REPO=ghcr.io/mentoredtestbed/
ARG BASE_IMAGE=mentored-base
ARG BASE_IMAGE_TAG=latest
FROM $BASE_REPO$BASE_IMAGE:$BASE_IMAGE_TAG

# Install dnsmasq
RUN apt-get update && \
    apt-get install -y dnsmasq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configure dnsmasq
RUN echo "listen-address=0.0.0.0" > /etc/dnsmasq.conf && \
    echo "bind-interfaces" >> /etc/dnsmasq.conf && \
    echo "no-hosts" >> /etc/dnsmasq.conf && \
    echo "addn-hosts=/etc/hosts" >> /etc/dnsmasq.conf && \
    echo "server=8.8.8.8" >> /etc/dnsmasq.conf  # Replace with preferred upstream DNS server if needed

# Expose DNS port
EXPOSE 53/udp
EXPOSE 53/tcp

# Start dnsmasq in the foreground
CMD ["dnsmasq", "--no-daemon"]