#!/bin/sh

set -eu

cd /helfertool/src

mkdir -p /data/media

export HELFERTOOL_CONFIG_FILE="/data/helfertool.yaml"

python3 manage.py migrate --noinput

exec supervisord --nodaemon --configuration /helfertool/supervisord.conf
