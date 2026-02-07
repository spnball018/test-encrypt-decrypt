#!/bin/sh

mkdir -p /etc/nginx/certs

if [ ! -f /etc/nginx/certs/selfsigned.crt ]; then
    echo "Generating self-signed certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/certs/selfsigned.key \
        -out /etc/nginx/certs/selfsigned.crt \
        -subj "/C=US/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"
fi

exec "$@"
