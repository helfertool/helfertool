# Install

It is recommended to use virtualenv:

    virtualenv helfertool
    cd helfertool
    . ./bin/activate

    git clone git@git.fs.tum.de:helfertool/helfertool.git

## Dependencies

### Software

 * Python 3
 * pdflatex (from TeX Live)
 * Redis or RabbitMQ (RabbitMQ is recommended)
 * DB software that is supported by Django (use SQLite for development)

### Python modules

The required Python modules are listed in the file requirements.txt, install
it with pip:

    pip install -r requirements.txt

For development some more modules may be useful:

    pip install -r requirements_dev.txt

### LaTeX packages

These packages or parts of LaTeX are necessary to use the default badge
template:

 * TikZ
 * grffile
 * ifthen
 * ulem
 * makebarcode

These packages are included in TeX Live and should be installed anyway.

## Run for development

### Celery and RabbitMQ

Since the software uses Celery you need one of supported message brokers, for
development we use RabbitMQ with Docker (note: the RabbitMQ server listens on
port 5672 to every incoming connection, you should configure a firewall):

    docker run -d --hostname helfertool-rabbitmq --name helfertool-rabbitmq \
        -p 5672:5672 rabbitmq

To start the RabbitMQ server later:

    docker start helfertool-rabbitmq

And start celery:

    celery -A helfertool worker -c 2 --loglevel=info

To update the RabbitMQ container later:

    docker pull rabbitmq
    docker stop helfertool-rabbitmq
    docker rm helfertool-rabbitmq
    docker run -d --hostname helfertool-rabbitmq --name helfertool-rabbitmq \
        -p 5672:5672 rabbitmq


### Django

By default Django uses a SQLite database that can be generated using the
following command inside the project directory:

    python manage.py migrate

Then a superuser should be created:

    python manage.py createsuperuser

Now you can start the webserver for development:

    python manage.py runserver

Now visit http://localhost:8000 with your browser.

### Mails

If you want to test the E-Mail part, you can start a SMTP debug server using
this command:

    python -m smtpd -n -c DebuggingServer localhost:1025

Additionally uncomment the following lines in `helfertool/settings.py`:

    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025

## Deployment

There are a lot of possibilities to deploy a Django project. For
helfen.fs.tum.de Apache2, uWSGI and MySQL are used. See here for the webserver
part: https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/uwsgi/

Instead of installing uwsgi with pip we used the Debian repository.

The used uWSGI configuration is in `stuff/deployment/uwsgi.conf`. It uses
Python 3.4 and automatically reloads Celery when uWSGI is touch-reloaded.


# Command line interface

In addition to the CLI of Django this software provides these commands:

## openregistration

    python manage.py openregistration test

*test* is the URL name.

## closeregistration

    python manage.py closeregistration test

*test* is the URL name.

## Using at to open the registration

To open the registration for a event at a specific time, the at daemon can be
used:

    at '13:55 10/18/2015'

If you use a virtualenv you need a script like `stuff/bin/open-registration.sh`.

# LICENSE

Copyright (C) 2015  Sven Hertle

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
