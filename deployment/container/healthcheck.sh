#!/bin/bash

set -Eeo pipefail

IFS="
"

die () {
    echo "$1"
    exit 1
}

# check webserver (with a host header that is allowed)
cd /helfertool/src
host="$(/helfertool/venv/bin/python manage.py shell -c "from django.conf import settings ; print(settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else '')")"
curl --fail --silent --output /dev/null -H "Host: $host" http://localhost:8000 || die "Error on HTTP query"

# check supervisord
for line in $(supervisorctl -c /helfertool/run/supervisord.conf status) ; do
    status="$(echo "$line" | awk '{print $2}')"
    if [ "$status" != "RUNNING" ] ; then
        die "Not all services running"
    fi
done
