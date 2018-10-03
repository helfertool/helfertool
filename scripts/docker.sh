#!/bin/bash

set -e

# base directory
basedir="$(dirname "$(dirname "$(readlink -f "$0")")")"
cd "$basedir"

# build
if [ "$1" == "build" ] ; then
    docker build --no-cache --pull -t helfertool/helfertool .
# build
elif [ "$1" == "fastbuild" ] ; then
    docker build -t helfertool/helfertool .
# test
elif [ "$1" == "test" ] ; then
    docker run --rm \
        --name helfertool \
        -p8000:8000 \
        -v "$PWD/test/docker/data:/data" \
        -v "$PWD/test/docker/config:/config" \
        -v "$PWD/test/docker/log:/log" \
        helfertool/helfertool
# push
elif [ "$1" == "push" ] ; then
    docker push helfertool/helfertool
else
    echo "Commands: build, fastbuild, test, push"
    exit 1
fi
