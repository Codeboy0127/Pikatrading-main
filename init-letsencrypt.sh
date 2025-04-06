#!/bin/bash

# Replace these with your actual domain and email
domains=(pikatrading.com www.pikatrading.com)
email="raud.boss@gmail.com"
staging=1 # Set to 1 if you're testing your setup to avoid hitting request limits

# Create required directories
mkdir -p certbot/conf
mkdir -p certbot/www

# Start nginx
docker-compose up --force-recreate -d nginx

# Wait for nginx to start
echo "### Waiting for nginx to start..."
sleep 5

echo "### Requesting Let's Encrypt certificate for ${domains[*]} ..."

# Join domains for certbot command
domain_args=""
for domain in "${domains[@]}"; do
  domain_args="$domain_args -d $domain"
done

# Request the certificate
docker-compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    --email $email \
    $domain_args \
    --rsa-key-size 4096 \
    --agree-tos \
    --force-renewal \
    $([ $staging = 1 ] && echo '--staging') \
    --non-interactive" certbot

echo "### Reloading nginx ..."
docker-compose exec nginx nginx -s reload

echo "Certificate created! You can now access your site at https://pikatrading.com"
echo "Note: You will see a browser warning about the self-signed certificate - this is normal for local development" 