#!/usr/bin/env bash
echo "🍺  All logs are in /var/log/api"
echo "🚀  Starting gunicorn"
gunicorn --bind 0.0.0.0:8080 app:app --error-logfile /var/log/api/gunicorn_error.log --access-logfile /var/log/api/gunicorn_access.log --capture-output --enable-stdio-inheritance -k uvicorn.workers.UvicornWorker
echo "❌  If you see this, gunicorn has crashed. Check the logs (/var/log/api/gunicorn*.log)"