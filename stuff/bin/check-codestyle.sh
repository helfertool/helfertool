#!/bin/bash

MODULES="helfertool registration badges news gifts help mail inventory statistic"

RED="\x1b[31m"
GREEN="\x1b[32m"
BLUE="\x1b[34m"
RESET="\x1b[0m"

PEP8_IGNORES="E121,E123,E126,E226,E24,E704"  # defaults
PEP8_IGNORES="$PEP8_IGNORES,E402"

# base directory
basedir="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
cd "$basedir"

# modules given?
if [ "$#" -gt "0" ] ; then
    modules="$@"
else
    modules="$MODULES"
fi

# check each module
for m in $modules ; do
    # print module
    echo -ne "${GREEN}Checking module: $m${RESET}\t\t"

    # PEP8
    pep_output="$(pep8 --exclude migrations --ignore $PEP8_IGNORES $m 2>&1)"
    if [ -z "$pep_output" ] ; then
        pep_errors="0"
    else
        pep_errors="$(echo "$pep_output" | wc -l)"
    fi

    # pylint
    pylint_output="$(pylint --load-plugins pylint_django \
        --rcfile="$basedir/.pylintrc" --reports=n -E $m)"
    pylint_errors="$(echo "$pylint_output" | grep "^E:" | wc -l)"

    # print ok/failed
    module_failed=0
    if [ "$pep_errors" != "0" ] || [ "$pylint_errors" != "0" ] ; then
        echo -e "${RED}[failed]${RESET}"
        module_failed=1
    else
        echo -e "${GREEN}[ok]${RESET}"
        continue
    fi

    # PEP8 output
    if ! [ -z "$pep_output" ] ; then
        echo -e "${BLUE}PEP8${RESET}"
        echo "$pep_output"
    fi

    # pylint
    if ! [ -z "$pylint_output" ] ; then
        echo -e "${BLUE}pylint${RESET}"
        echo "$pylint_output"
    fi

    # summary
    if [ "$module_failed" == "1" ] ; then
        echo -e "${RED}PEP8: $pep_errors, pylint: $pylint_errors ${RESET}"
    fi
done
