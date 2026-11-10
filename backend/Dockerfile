
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

# GOST o'rnatish
RUN bash <(curl -fsSL https://github.com/go-gost/gost/raw/master/install.sh) --install \
    && command -v gost \
    && gost -V

# Python kutubxonalarini o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend fayllarini nusxalash
COPY . .

# Start script
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
