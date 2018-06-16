#!/bin/sh

python manage.py makemessages -i components -i doc -i requirements.txt -i requirements_dev.txt -i manage.py -l de
