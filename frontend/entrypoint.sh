#!/bin/sh
set -e

if [ "$USER_UID" = "" ]; then
    echo "USER_UID environment variable is not set. Defaulting to 101 (nginx)"
    USER_UID="101"
fi

if [ "$USER_GID" = "" ]; then
    echo "USER_GID environment variable is not set. Defaulting to 101 (nginx)"
    USER_GID="101"
fi

touch /var/run/nginx.pid
mkdir -p /var/cache/nginx /var/log/nginx
touch /var/log/nginx/error.log
touch /var/log/nginx/access.log
chown -R $USER_UID:$USER_GID /var/cache/nginx /var/run/nginx.pid /var/log/nginx
echo "Starting nginx"
echo "Logs will be written to /var/log/nginx/error.log and /var/log/nginx/access.log"
exec su-exec "$USER_UID:$USER_GID" nginx -g "daemon off;"

