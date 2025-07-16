#!/bin/sh 

hashes=$(grep -oE 'sha384-[a-zA-Z0-9+/=]*' dist/frontend/browser/index.html |  sed "s/^/'/" | sed "s/\$/'/" | tr '\n' ' ')

echo "events{}
http {
    include /etc/nginx/mime.types;
    access_log /app/log/access.log;
    error_log /app/log/error.log;


    server {
        listen 80;
        root /usr/share/nginx/html/frontend/browser;
        index index.html;
        add_header Content-Security-Policy \"default-src 'self'; style-src 'self' 'unsafe-inline'; object-src 'none' ; script-src $hashes; img-src 'self' https://icons.duckduckgo.com/; base-uri 'self'; frame-src 'self'; connect-src 'self' 'self' https://icons.duckduckgo.com/; manifest-src 'self'; worker-src 'self';\" always;

        location / {
            try_files \$uri \$uri/ /index.html;
        }
    }
}
" > nginx.conf