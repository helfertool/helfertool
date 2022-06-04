#!/bin/bash

set -Eeo pipefail

IFS="
"

die () {
    echo "$1"
    exit 1
}

# check webserver
curl --fail --silent --output /dev/null http://localhost:8000 || die "Error on HTTP query"

# check supervisord
for line in $(supervisorctl -c /helfertool/run/supervisord.conf status) ; do
    status="$(echo "$line" | awk '{print $2}')"
    if [ "$status" != "RUNNING" ] ; then
        die "Not all services running"
    fi
done
