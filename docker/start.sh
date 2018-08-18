#!/bin/bash

if [ -e "celeryd.pid" ]
then
	rm celeryd.pid
fi

python manage.py migrate

celery -A helfertool worker -D -c 2 --loglevel=info
python manage.py runserver --insecure 0.0.0.0:8000
