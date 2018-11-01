#!/bin/bash

set -e

# base directory
basedir="$(dirname "$(dirname "$(readlink -f "$0")")")"
cd "$basedir"

# get git branch and determine tag
git_branch="$(git rev-parse --abbrev-ref HEAD)"

if [ "$git_branch" == "master" ] ; then
    docker_tag="helfertool/helfertool:latest"
else
    docker_tag="helfertool/helfertool:$git_branch"
fi

# build
if [ "$1" == "build" ] ; then
    docker build --no-cache --pull -t "$docker_tag" .
# fastbuild
elif [ "$1" == "fastbuild" ] ; then
    docker build -t "$docker_tag" .
# test
elif [ "$1" == "test" ] ; then
    docker run --rm \
        --name helfertool \
        -p8000:8000 \
        -v "$PWD/test/docker/data:/data" \
        -v "$PWD/test/docker/config:/config" \
        -v "$PWD/test/docker/log:/log" \
        "$docker_tag"
# push
elif [ "$1" == "push" ] ; then
    docker push "$docker_tag"
# pushlatest
elif [ "$1" == "pushlatest" ] ; then
    docker tag "$docker_tag" "helfertool/helfertool:latest"
    docker push "helfertool/helfertool:latest"
else
    echo -e "Usage:"
    echo
    echo -e "build\t\tBuild clean image"
    echo -e "fastbuild\tBuild image using cached layers"
    echo
    echo -e "test\t\tRun docker container with test data"
    echo
    echo -e "push\t\tPush container for current branch to docker hub"
    echo -e "publishdev\tPush current container as \"latest\" to docker hub"

    exit 1
fi
