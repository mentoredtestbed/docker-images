ARG BASE_REPO=ghcr.io/mentoredtestbed/
ARG BASE_IMAGE_TAG=latest

# Stage 1: Build the SSL certificate using OpenSSL
FROM debian:bookworm AS builder

# Install OpenSSL in the builder image
RUN apt-get update && apt-get install -y openssl && rm -rf /var/lib/apt/lists/*

# Set environment variables for certificate details
ENV CERT_DIR=/etc/ssl/certs
ENV PRIVATE_KEY_DIR=/etc/ssl/private
ENV CERT_NAME=server
ENV COUNTRY=US
ENV STATE=California
ENV CITY=SanFrancisco
ENV ORG="MENTORED TESTBED TEST CERT"
ENV CN="localhost"

# Create directories for SSL certificate and key
RUN mkdir -p ${CERT_DIR} ${PRIVATE_KEY_DIR}

# Generate SSL private key
RUN openssl genrsa -out ${PRIVATE_KEY_DIR}/${CERT_NAME}.key 2048

# Generate self-signed SSL certificate
RUN openssl req -new -x509 -key ${PRIVATE_KEY_DIR}/${CERT_NAME}.key \
  -out ${CERT_DIR}/${CERT_NAME}.crt \
  -days 365 \
  -subj "/C=${COUNTRY}/ST=${STATE}/L=${CITY}/O=${ORG}/CN=${CN}"




FROM $BASE_REPO"nginx-simple":$BASE_IMAGE_TAG

# Copy the SSL certificate and key from the builder stage
COPY --from=builder /etc/ssl/certs/server.crt /etc/ssl/certs/
COPY --from=builder /etc/ssl/private/server.key /etc/ssl/private/

# Create the Nginx config for SSL
RUN mkdir -p /etc/nginx/conf.d
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx.reverseproxy.conf /etc/nginx/nginx.reverseproxy.conf.disabled
COPY setup-reverse-proxy.sh /usr/local/bin/setup-reverse-proxy.sh

# Expose HTTPS port
EXPOSE 443

# Start Nginx in the foreground (needed for Docker)
CMD ["nginx", "-g", "daemon off;"]
