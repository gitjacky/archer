#!/bin/bash

settings=${1:-"archer.settings"}
ip=${2:-"0.0.0.0"}
port=${3:-8000}

nohup gunicorn -t 1200 -w 4 --env DJANGO_SETTINGS_MODULE=${settings} --error-logfile=/tmp/archer.err -b ${ip}:${port} archer.wsgi:application &
#gunicorn -w 2 -k gevent --error-logfile=/tmp/archer.err -b ${ip}:${port} archer.wsgi:application &
