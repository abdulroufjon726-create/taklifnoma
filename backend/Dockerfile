FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl bash iproute2 iptables \
    && rm -rf /var/lib/apt/lists/*

# Tailscale
RUN curl -fsSL https://tailscale.com/install.sh | sh

# GOST
RUN curl -fsSL https://github.com/go-gost/gost/raw/master/install.sh \
    -o /tmp/gost-install.sh \
    && bash /tmp/gost-install.sh --install \
    && rm /tmp/gost-install.sh

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
