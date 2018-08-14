#!/bin/bash

set -e

# base directory
basedir="$(dirname "$(dirname "$(readlink -f "$0")")")"
cd "$basedir"

# build
if [ "$1" == "build" ] ; then
    docker build --no-cache -t helfertool/helfertool .
# build
elif [ "$1" == "fastbuild" ] ; then
    docker build -t helfertool/helfertool .
# push
elif [ "$1" == "push" ] ; then
    docker push helfertool/helfertool
else
    echo "Commands: build, fastbuild, push"
    exit 1
fi
