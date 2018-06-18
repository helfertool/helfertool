#!/bin/sh


# input parameters
if [ -z "$HELFERTOOL_WORKERS" ] ; then
    export HELFERTOOL_WORKERS="$(( 2 * $(nproc --all) ))"
fi

if [ -z "$HELFERTOOL_TASK_WORKERS" ] ; then
    task_workers="$(( $(nproc --all) / 2 ))"
    if [ "$task_workers" == "0" ] ; then
        task_workers=1
    fi

    export HELFERTOOL_TASK_WORKERS="$task_workers"
fi

echo "Running with $HELFERTOOL_WORKERS web and $HELFERTOOL_TASK_WORKERS task workers"

# prepare environment
set -eu

cd /helfertool/src
mkdir -p /data/media

export HELFERTOOL_CONFIG_FILE="/data/config/helfertool.yaml"

# migrations and run
python3 manage.py migrate --noinput

exec supervisord --nodaemon --configuration /helfertool/supervisord.conf
