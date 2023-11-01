#!/usr/bin/env bash
echo "⚡️  Starting gunicorn"
gunicorn --bind 0.0.0.0:8080 app:app --log-level debug --error-logfile /var/log/api/gunicorn_error.log --access-logfile /var/log/api/gunicorn_access.log --capture-output --enable-stdio-inheritance
echo "🚀  API started"
echo "🍺  All logs are in /var/log/api"