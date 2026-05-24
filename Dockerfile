FROM debian:12-slim

LABEL maintainer="Inventions4All - github:TWeb79"
LABEL description="NeuroSync - Adaptive Brainwave Audio Studio"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    portaudio19-dev \
    libsndfile1 \
    qt6-base-dev \
    python3-dev \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python3", "-m", "neurosync.app.main"]