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


if [ "$USER" = "" ]; then
    echo "USER environment variable is not set. Defaulting to 1001:1001"
    USER="1001:1001"
fi


chown -R $USER:$USER /api/logs

###
# Switch to user 1001 and execute the main script
###

exec gosu $USER:$USER start.sh