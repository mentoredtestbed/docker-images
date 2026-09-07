ARG BASE_REPO=ghcr.io/mentoredtestbed/
ARG BASE_IMAGE=mentored-base
ARG BASE_IMAGE_TAG=latest
FROM $BASE_REPO$BASE_IMAGE:$BASE_IMAGE_TAG

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/logs
RUN rm -rf /app/logs/*
CMD ["python", "server.py"]
