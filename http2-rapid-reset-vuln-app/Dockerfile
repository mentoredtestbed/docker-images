ARG BASE_REPO=ghcr.io/mentoredtestbed/
ARG BASE_IMAGE=mentored-base
ARG BASE_IMAGE_TAG=latest
FROM $BASE_REPO$BASE_IMAGE:$BASE_IMAGE_TAG

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# install flask and jsonify
RUN pip install --break-system-packages flask 

COPY ./vuln-app.py /usr/local/bin/vuln-app.py

# Start Nginx in the foreground (needed for Docker)
CMD ["python3", "/usr/local/bin/vuln-app.py"]
