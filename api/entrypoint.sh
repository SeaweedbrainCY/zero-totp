#!/usr/bin/env bash

####
# Pre-execution set up 
# User: root
####

set -e 

mkdir -p /api/logs 
touch /api/logs/api.log
touch /api/logs/gunicorn_error.log
touch /api/logs/gunicorn_access.log


if [ "$USER_UID" = "" ]; then
    echo "USER_UID environment variable is not set. Defaulting to 1001"
    USER_UID="1001"
fi

if [ "$USER_GID" = "" ]; then
    echo "USER_GID environment variable is not set. Defaulting to 1001"
    USER_GID="1001"
fi


chown -R $USER:$USER /api/logs

###
# Switch to user 1001 and execute the main script
###

exec gosu $USER:$USER ./start.sh "$@"