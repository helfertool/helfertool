#!/bin/bash

basedir="$(dirname "$(dirname "$(readlink -f "$0")")")"

python=$(wc -l $(find "$basedir/helfertool" "$basedir/registration" "$basedir/badges" "$basedir/news" -iname '*.py') | tail -n 1 | awk '{print $1}')
html=$(wc -l $(find "$basedir/helfertool" "$basedir/registration" "$basedir/badges" "$basedir/news" -iname '*.html') | tail -n 1 | awk '{print $1}')

echo "Python: $python"
echo "HTML:   $html"
echo
echo "Summe:  $((python + html))"
