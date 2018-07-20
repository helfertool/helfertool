#!/bin/bash

set -e

# base directory
basedir="$(dirname "$(dirname "$(readlink -f "$0")")")"
cd "$basedir"

# build
if [ "$1" == "build" ] ; then
    docker build -t helfertool/helfertool .
# push
elif [ "$1" == "push" ] ; then
    docker push helfertool/helfertool
else
    echo "Commands: build, push"
    exit 1
fi
