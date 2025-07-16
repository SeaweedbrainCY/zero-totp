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
chown -R $USER_UID:$USER_GID /var/cache/nginx /var/run/nginx.pid /var/log/nginx
echo "Starting nginx ..."
exec su-exec "$USER_UID:$USER_GID" nginx -g "daemon off;"

