FROM alpine:latest

RUN apk add --no-cache python3 py3-pip nginx curl unzip jq bash tzdata

WORKDIR /app
COPY requirements.txt .

# Install dependencies
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Install Xray-core
RUN wget -O xray.zip "https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip" && \
    unzip xray.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/xray && \
    rm xray.zip

# Copy application files
COPY . /app

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Entrypoint setup
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
