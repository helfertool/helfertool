#!/bin/sh

set -eu

#
# settings and base directory
#
container_name="docker.io/helfertool/helfertool"

basedir="$(dirname "$(dirname "$(readlink -f "$0")")")"
cd "$basedir"

#
# get git branch and tag, derive container tag -> results in the following
# variables being set
#
container_tag=""
container_update_latest=0
container_prevent_push=0

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

if [ "$git_branch" = "main" ] ; then
    # we are on main -> do a stable release and update the latest tag
    container_tag="$(get_release_series)"
    container_update_latest=1
elif [ "$(echo "$git_branch" | grep "^lts/")" != "" ] ; then
    # we are on a lts branch -> stable release, but do not update latest tag
    container_tag="$(get_release_series)"
elif [ "$git_branch" = "dev" ] ; then
    # dev branch: just push to dev, thats it
    container_tag="dev"
else
    # other branch: build is fine, but do not push
    echo "Current branch is $git_branch. container must not be pushed!"
    container_tag="$(echo "$git_branch" | tr '/' '-')"
    container_prevent_push=1
fi

#
# check what action should be done and to it
#
set +u
action="$1"
set -u

# command: build
if [ "$action" = "build" ] ; then
    # build without cache and with updated base image
    container_version="$(date -u -Iseconds)"
    podman build --no-cache --pull \
        --arch=amd64 \
        --build-arg CONTAINER_VERSION="$container_version" \
        --format docker \
        -t "$container_name:$container_tag" .

# command: fastbuild
elif [ "$action" = "fastbuild" ] ; then
    # build with cache, as fast as possible
    podman build \
        --arch=amd64 \
        --build-arg CONTAINER_VERSION="fastbuild" \
        --format docker \
        -t "$container_name:$container_tag" .

    echo ""
    echo "Warning: fastbuild should not be done for releases"

# command: test
elif [ "$action" = "test" ] ; then
    # run container with test data, listen on port 8000
    podman run --rm \
        --name helfertool \
        --user "$(id -u):$(id -g)" \
        --userns keep-id \
        --read-only \
        --volume "$PWD/test/container/config:/config" \
        --volume "$PWD/test/container/data:/data" \
        --volume "$PWD/test/container/log:/log" \
        --tmpfs "/helfertool/run" \
        --publish 8000:8000 \
        "$container_name:$container_tag"

# command: autotest
elif [ "$action" = "autotest" ] ; then
    # run container with test data, listen on port 8000
    echo "Running container..."
    podman run --detach \
        --rm \
        --name helfertool \
        --user "$(id -u):$(id -g)" \
        --userns keep-id \
        --read-only \
        --volume "$PWD/test/container/config:/config" \
        --volume "$PWD/test/container/data:/data" \
        --volume "$PWD/test/container/log:/log" \
        --tmpfs "/helfertool/run" \
        --publish 8000:8000 \
        "$container_name:$container_tag"

    sleep 10

    set +e
    echo "Running healthcheck..."
    podman healthcheck run helfertool
    healthcheck_return_code="$?"
    set -e

    echo "Stopping container..."
    podman stop helfertool

    if [ "$healthcheck_return_code" != "0" ] ; then
        echo "\nFAILED"
    else
        echo "\nPASSED"
    fi
    exit $healthcheck_return_code

# command: push
elif [ "$action" = "push" ] ; then
    # push
    if [ "$container_prevent_push" = "1" ] ; then
        exit 1
    fi

    podman push "$container_name:$container_tag"

    if [ "$container_update_latest" = "1" ] ; then
        podman tag "$container_name:$container_tag" "$container_name:latest"
        podman push "$container_name:latest"
    fi

# help message
else
    echo "Usage:"
    echo
    echo "build\t\tBuild clean image"
    echo "fastbuild\tBuild image using cached layers"
    echo
    echo "test\t\tRun container with test data"
    echo "autotest\tRun container, health check and exit"
    echo
    echo "push\t\tPush container for current branch to container registry"

    exit 1
fi
