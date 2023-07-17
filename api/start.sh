#!/usr/bin/env bash
gunicorn --bind 0.0.0.0:7777 app:app
