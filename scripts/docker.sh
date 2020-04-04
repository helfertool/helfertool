#!/bin/sh

set -eu

#
# settings and base directory
#
docker_name="helfertool/helfertool"

basedir="$(dirname "$(dirname "$(readlink -f "$0")")")"
cd "$basedir"

#
# get git branch and tag, derive docker tag -> results in the following
# variables being set
#
docker_tag=""
docker_update_latest=0
docker_prevent_push=0

# get version from git and do sanity check with version.txt, returns release series
get_release_series()
{
    version="$(git describe --abbrev=0 | sed 's/^v//g')"

    # sanity check: is the version.txt file the same?
    file_version="$(cat src/version.txt)"
    if [ "$version" != "$file_version" ] ; then
        echo "Version from git and version.txt inconsistent!" >&2
        exit 1
    fi

    echo "$version" | sed 's/\.[0-9]*$/.x/'
}

# behavior depends on branch
git_branch="$(git rev-parse --abbrev-ref HEAD)"

if [ "$git_branch" = "master" ] ; then
    # we are on master -> do a stable release and update the latest tag
    docker_tag="$(get_release_series)"
    docker_update_latest=1
elif [ "$(echo "$git_branch" | grep "^lts/")" != "" ] ; then
    # we are on a lts branch -> stable release, but do not update latest tag
    docker_tag="$(get_release_series)"
elif [ "$git_branch" = "dev" ] ; then
    # dev branch: just push to dev, thats it
    docker_tag="dev"
else
    # other branch: build is fine, but do not push
    echo "Current branch is $git_branch. Docker container must not be pushed!"
    docker_tag="$git_branch"
    docker_prevent_push=1
fi

#
# check what action should be done and to it
#
set +u
action="$1"
set -u

if [ "$action" = "build" ] ; then
    # build without cache and with updated base image
    container_version="$(date --utc --iso-8601=seconds)"
    docker build --no-cache --pull \
        --build-arg CONTAINER_VERSION="$container_version" \
        -t "$docker_name:$docker_tag" .
elif [ "$action" = "fastbuild" ] ; then
    # build with cache, as fast as possible
    container_version="$(date --utc --iso-8601=seconds)"
    docker build \
        --build-arg CONTAINER_VERSION="$container_version" \
        -t "$docker_name:$docker_tag" .

    echo ""
    echo "Warning: fastbuild should not be done for releases"
elif [ "$action" = "test" ] ; then
    # run container with test data, listen in port 8000
    docker run --rm \
        --name helfertool \
        -p8000:8000 \
        -v "$PWD/test/docker/data:/data" \
        -v "$PWD/test/docker/config:/config" \
        -v "$PWD/test/docker/log:/log" \
        "$docker_name:$docker_tag"
elif [ "$action" = "push" ] ; then
    # push
    if [ "$docker_prevent_push" = "1" ] ; then
        exit 1
    fi

    docker push "$docker_name:$docker_tag"

    if [ "$docker_update_latest" = "1" ] ; then
        docker tag "$docker_name:$docker_tag" "$docker_name:latest"
        docker push "$docker_name:latest"
    fi
else
    echo "Usage:"
    echo
    echo "build\t\tBuild clean image"
    echo "fastbuild\tBuild image using cached layers"
    echo
    echo "test\t\tRun docker container with test data"
    echo
    echo "push\t\tPush container for current branch to docker hub"

    exit 1
fi
