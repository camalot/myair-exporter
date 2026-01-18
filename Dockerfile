FROM python:3.13-alpine

ARG BRANCH="develop"
ARG BUILD_VERSION="1.0.0-snapshot"
ARG PROJECT_NAME=

ENV PYTHONUNBUFFERED=0
ENV APP_VERSION=${BUILD_VERSION}

LABEL VERSION="${BUILD_VERSION}"
LABEL BRANCH="${BRANCH}"
LABEL PROJECT_NAME="${PROJECT_NAME}"

# Create and activate virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
COPY ./ /app/
RUN \
  apk update && \
  apk add --no-cache git curl build-base tcl tk && \
  mkdir -p /data && \
  pip install --no-cache-dir --upgrade pip && \
  pip install --no-cache-dir . && \
  sed -i "s/APP_VERSION = \"1.0.0-snapshot\"/APP_VERSION = \"${APP_VERSION}\"/g" "/app/libs/settings.py" && \
  apk del git build-base

VOLUME ["/data"]
VOLUME ["/config"]

EXPOSE 8933

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:8933/health || exit 1

CMD ["python", "-u", "/app/main.py"]
