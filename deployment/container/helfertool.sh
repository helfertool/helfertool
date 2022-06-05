#!/bin/bash

set -Eeo pipefail

die () {
    echo "$1"
    exit 1
}

# check that we do not run as root
if [ "$(id -u)" = "0" ] ; then
    die "Running as root in container. Exiting."
fi

# check if we can write into /logs, /data and /helfertool/run
touch /log/.test 2>/dev/null || die "Cannot write to log directory. Exiting."
rm -f /log/.test

touch /data/.test 2>/dev/null || die "Cannot write to data directory. Exiting."
rm -f /data/.test

touch /helfertool/run/.test 2>/dev/null || die "Cannot write to tmp directory (/helfertool/run in container). Exiting."
rm -f /helfertool/run/.test

# check if /config/helfertool.yaml is there
if ! [ -f /config/helfertool.yaml ] ; then
    die "helfertool.yaml is missing. Exiting."
fi

# prepare environment
cd /helfertool/src
mkdir -p /data/media /data/tmp /helfertool/run/tmp

# command: init
if [ "$1" = "init" ] ; then
    # initialise database with default settings
    python3 manage.py loaddata toolsettings

# command: reload
elif [ "$1" = "reload" ] ; then
    # reload uwsgi and celery
    touch /helfertool/run/uwsgi_reload

    if [ -f "/helfertool/run/celery.pid" ] ; then
        kill -HUP $(cat /helfertool/run/celery.pid)
    fi

# command: postrotate
elif [ "$1" = "postrotate" ] ; then
    if [ -f "/helfertool/run/rsyslog.pid" ] ; then
        kill -HUP $(cat /helfertool/run/rsyslog.pid)
    fi

# command: manage
elif [ "$1" = "manage" ] ; then
    shift
    python3 manage.py $@

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

    # create some directories and files that we need
    mkdir -p /helfertool/run/supervisord /helfertool/run/nginx
    touch /var/log/nginx/error.log  # /var/log/nginx/error.log is a symlink to this file

    # set random password for supervisord unix socket
    sed "s/will_be_replaced/$(pwgen 40 1)/g" /helfertool/etc/supervisord.conf > /helfertool/run/supervisord.conf

    # run migrations and go
    python3 manage.py migrate --noinput
    python3 manage.py createcachetable
    exec supervisord --nodaemon --configuration /helfertool/run/supervisord.conf

# help message
else
    die "Commands: init, createadmin, reload, postrotate, run, manage"
fi
