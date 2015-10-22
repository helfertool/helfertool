#!/bin/sh

DIR="/home/hertle/Programmieren/helfertool"
PROJECT_DIR="helfertool"
EVENT="test"

cd "$DIR"
. ./bin/activate
cd "$PROJECT_DIR"
python manage.py openregistration "$EVENT"
