#!/bin/sh

# prepare environment
cd /helfertool/src
mkdir -p /data/media
export HELFERTOOL_CONFIG_FILE="/config/helfertool.yaml"

# command: init
if [ "$1" = "init" ] ; then
    # initialise database with default settings
    python3 manage.py migrate --noinput
    python3 manage.py loaddata toolsettings
    python3 manage.py createsuperuser

# command: newadmin
elif [ "$1" = "newadmin" ] ; then
    # create new superuser
    python3 manage.py createsuperuser

# command: run
elif [ "$1" = "run" ] ; then
    # input parameters
    if [ -z "$HELFERTOOL_WORKERS" ] ; then
        export HELFERTOOL_WORKERS="$(( 2 * $(nproc --all) ))"
    fi

    if [ -z "$HELFERTOOL_TASK_WORKERS" ] ; then
        task_workers="$(( $(nproc --all) / 2 ))"
        if [ "$task_workers" = "0" ] ; then
            task_workers=1
        fi

        export HELFERTOOL_TASK_WORKERS="$task_workers"
    fi

    echo "Running with $HELFERTOOL_WORKERS web and $HELFERTOOL_TASK_WORKERS task workers"

    # run migrations and go
    python3 manage.py migrate --noinput
    exec supervisord --nodaemon --configuration /helfertool/supervisord.conf

# help message
else
    echo "Commands: init, newadmin, run"
    exit 1
fi
