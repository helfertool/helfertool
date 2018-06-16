#!/bin/sh

set -eu

cd /helfertool/src

mkdir -p /data/media

python3 manage.py migrate --noinput

python3 manage.py runserver 0.0.0.0:1234
