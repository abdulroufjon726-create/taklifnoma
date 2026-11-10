
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Kerakli tizim paketlari
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    bash \
    iproute2 \
    iptables \
    && rm -rf /var/lib/apt/lists/*

# Tailscale o'rnatish
RUN curl -fsSL https://tailscale.com/install.sh | sh



# GOST 3.3.2 o'rnatish
RUN curl -fL \
    https://github.com/go-gost/gost/releases/download/v3.3.2/gost_3.3.2_linux_amd64.tar.gz \
    -o /tmp/gost.tar.gz \
    && tar -tzf /tmp/gost.tar.gz \
    && tar -xzf /tmp/gost.tar.gz -C /usr/local/bin gost \
    && chmod +x /usr/local/bin/gost \
    && gost -V \
    && rm /tmp/gost.tar.gz



# Python kutubxonalarini o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend fayllarini nusxalash
COPY . .

# Start script
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
