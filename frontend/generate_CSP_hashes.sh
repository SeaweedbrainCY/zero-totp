#!/bin/sh 

hashes=$(grep -oE 'sha384-[a-zA-Z0-9+/=]*' dist/frontend/browser/index.html |  sed "s/^/'/" | sed "s/\$/'/" | tr '\n' ' ')

echo "
events{}
http {
    include /etc/nginx/mime.types;
    server {
        listen 80;
        root /usr/share/nginx/html/frontend/browser;
        index index.html;
        add_header Content-Security-Policy \"default-src https://*.zero-totp.com; style-src 'self' 'unsafe-inline'; object-src 'none' ; script-src $hashes ; img-src 'self' https://icons.duckduckgo.com/; base-uri 'self'; frame-src 'self'; connect-src 'self' https://*.zero-totp.com; manifest-src 'self'\" always;

        location / {
            try_files $uri $uri/ /index.html;
        }
    }
}
"