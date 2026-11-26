FROM python:3.12-slim

LABEL maintainer="videoflix@example.com"
LABEL version="1.0"
LABEL description="Python 3.12 Alpine Linux"

WORKDIR /app

COPY . .

RUN apt-get update && \
    apt-get install -y --no-install-recommends bash postgresql-client ffmpeg build-essential && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    chmod +x backend.entrypoint.sh

WORKDIR /app/videoflix

EXPOSE 8000

ENTRYPOINT [ "../backend.entrypoint.sh" ]
