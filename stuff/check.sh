#!/bin/bash

MODULES="helfertool registration badges"

GREEN="\x1b[32m"
RED="\x1b[31m"
RESET="\x1b[0m"

PEP8_IGNORES="E121,E123,E126,E226,E24,E704"  # defaults
PEP8_IGNORES="$PEP8_IGNORES,E402"

for m in $MODULES ; do
    # print module
    echo -ne "${GREEN}Checking module: $m${RESET}\t\t"

    # PEP8
    pep_output="$(pep8 --exclude migrations --count --ignore $PEP8_IGNORES $m 2>&1)"
    pep_errors="$(echo "$pep_output" | tail -n 1)"

    # print ok/failed
    if ! [ -z "$pep_errors" ] && [ "$pep_errors" -gt "0" ] ; then
        echo -e "${RED}[failed]${RESET}"
    else
        echo -e "${GREEN}[ok]${RESET}"
        continue
    fi

    # PEP8 output
    echo "$pep_output" | head -n -1
    echo -e "${RED}$pep_errors Errors${RESET}"
done
