#!/usr/bin/env bash

if [ "$1" = "auto-upgrade" ]; then
    echo "🔄 Auto upgrade asked. Use this option with precaution"
    alembic upgrade head
    if [ $? -eq 0 ]; then
        echo "✅ Database updated successfully"
    else
        echo "❌ An error occurred while updating the database. Check the error message above to understand what happened."
        exit 1
    fi
fi


alembic check > /tmp/alembic_check.log 2>&1
if [ $? -eq 0 ]; then 
    cat /tmp/alembic_check.log > /var/log/api/api.log
    echo "🎉  Your database is up to date."
elif cat /tmp/alembic_check.log | grep "Target database is not up to date."; then
   echo "❌  Your database is not up to date. Follow Zero-TOTP's documentation to update it."
    echo "📚 https://docs.zero-totp.com"
    echo "🕛 Docker will wait for your action to continue"
    tail -f /dev/null
else
    cat /tmp/alembic_check.log
    echo "❌  An error occurred while starting the API. Check the error message above to understand what happened. Docker will restart now."
    exit 1
fi
echo "🍺  All logs are in /var/log/api"
echo "🚀  Starting gunicorn"
gunicorn --bind 0.0.0.0:8080 app:app --error-logfile /var/log/api/gunicorn_error.log --access-logfile /var/log/api/gunicorn_access.log --capture-output --enable-stdio-inheritance -k uvicorn.workers.UvicornWorker
echo "❌  If you see this, gunicorn has crashed. Check the logs (/var/log/api/gunicorn*.log)"