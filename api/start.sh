#!/usr/bin/env bash
gunicorn --bind 0.0.0.0:8080 app:app --log-level debug --error-logfile /var/log/gunicorn_error.log --access-logfile /var/log/gunicorn_access.log --capture-output --enable-stdio-inheritance
