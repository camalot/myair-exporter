FROM python:3.13-alpine

ARG BRANCH="develop"
ARG BUILD_VERSION="1.0.0-snapshot"
ARG PROJECT_NAME=

ENV PYTHONUNBUFFERED=0
ENV APP_VERSION=${BUILD_VERSION}

LABEL VERSION="${BUILD_VERSION}"
LABEL BRANCH="${BRANCH}"
LABEL PROJECT_NAME="${PROJECT_NAME}"

COPY ./ /app/
RUN \
  apk update && \
  apk add --no-cache git curl build-base tcl tk && \
  mkdir -p /app /data && \
  pip install --no-cache-dir --upgrade pip && \
  pip install --no-cache-dir -r /app/setup/requirements.txt && \
  sed -i "s/APP_VERSION = \"1.0.0-snapshot\"/APP_VERSION = \"${APP_VERSION}\"/g" "/app/libs/settings.py" && \
  apk del git build-base && \
  rm -rf /app/setup

VOLUME ["/data"]
VOLUME ["/config"]
WORKDIR /app

CMD ["python", "-u", "/app/main.py"]
