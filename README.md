# Install

## Dependencies

 * Python 3
 * Bower (depends on node and npm)
 * pdflatex (from TeX Live)
 * Redis or RabbitMQ (RabbitMQ is recommended)
 * DB software that is supported by Django (use SQLite for development)

## Setup environment

It is recommended to use a Python virtual environment:

    pyvenv helfertool
    cd helfertool

    npm install bower
    # fix so that bower is found inside the virtualenv
    ln -s "$(pwd)/node_modules/bower/bin/bower" "bin/bower"

    . ./bin/activate

    git clone git@git.fs.tum.de:helfertool/helfertool.git

## Python modules

The required Python modules are listed in the file requirements.txt, install
it with pip:

    pip install -r requirements.txt

For development some more modules may be useful:

    pip install -r requirements_dev.txt

Since you probably will not use SQLite in your live system you have to install
the python module for your database:
https://docs.djangoproject.com/en/dev/ref/databases/

For MySQL we use mysqlclient which is also recommended by Django.

## Bower packages

To install the necessary CSS and JS libraries, execute:

   python manage.py bower install

## LaTeX packages

These packages or parts of LaTeX are necessary to use the default badge
template:

 * TikZ
 * grffile
 * ifthen
 * ulem
 * makebarcode

These packages are included in TeX Live and should be installed anyway.

## Set secret key

You have to set a secret key in the configuration file
`helfertool/settings.py`:

    SECRET_KEY = 'CHANGE-ME-AFTER-INSTALL'

You can generate a new key using the script `./stuff/bin/gen-secret-key.py`.

## Database

The database configuration is done in `helfertool/settings.py`:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

Look at https://docs.djangoproject.com/en/dev/ref/databases/ for examples
how to configure Django to use an other database.

Now you should run the database migrations:

    python manage.py migrate

## Celery

Since the software uses Celery you need one of supported message brokers, we
use RabbitMQ for development and deployment.

### Deployment
For deployment we installed RabbitMQ using the package repository.

### Development
For development, RabbitMQ is installed using Docker (note: the RabbitMQ server
listens on port 5672 to every incoming connection, you should configure a
firewall):

    docker run -d --hostname helfertool-rabbitmq --name helfertool-rabbitmq \
        -p 5672:5672 rabbitmq

To start the RabbitMQ server later:

    docker start helfertool-rabbitmq

To update the RabbitMQ container later:

    docker pull rabbitmq
    docker stop helfertool-rabbitmq
    docker rm helfertool-rabbitmq
    docker run -d --hostname helfertool-rabbitmq --name helfertool-rabbitmq \
        -p 5672:5672 rabbitmq

### Configuration and start

Change the broker configuration in `helfertool/settings.py`.

For RabbitMQ with the username "guest" and password "guest" the configuration
should look like this:

    BROKER_URL = 'amqp://guest:guest@127.0.0.1/'
    CELERY_RESULT_BACKEND = 'amqp://guest:guest@127.0.0.1/'

Now start celery:

    celery -A helfertool worker -c 2 --loglevel=info

## Mails

The Helfertool tries to send mails to localhost:25 with the default
configuration.

If you want to test the E-Mail part during development, you can start a
SMTP debug server using this command:

    python -m smtpd -n -c DebuggingServer localhost:1025

Additionally uncomment the following lines in `helfertool/settings.py`:

    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025

## Create superuser

Now a superuser should be created:

    python manage.py createsuperuser

## Create git branch for local configuration

To make further updates easier it is a good idea to put the changes in a new
branch called "local" here:

    git stash
    git stash branch local
    git commit -a -m "Modified configuration"

You should not push this branch to any server since it contains you database
password!

At the end you should also make sure that the configuration is not readable
for all users:

    chmod 640 helfertool/settings.py

# Run for development

For development the following steps should be done:

Start RabbitMQ:

    docker start helfertool-rabbitmq

Start celery:

    celery -A helfertool worker -c 2 --loglevel=info

Start the webserver for development:

    python manage.py runserver

Now visit http://localhost:8000 with your browser.

# Deployment

There are a lot of possibilities to deploy a Django project. For
helfen.fs.tum.de Apache2, uWSGI and MySQL are used. See here for the webserver
part: https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/uwsgi/

Instead of installing uwsgi with pip we used the Debian repository.

The used uWSGI configuration is in `stuff/deployment/uwsgi.conf`. It uses
Python 3.4 and automatically reloads Celery when uWSGI is touch-reloaded.

# Upgrades

There are a few steps to update a instance of the helfertool, assuming you
followed the steps above:

    # entern virtual env
    . ./bin/activate
    cd helfertool

    # update source code
    git checkout master
    git pull
    git checkout local
    git merge master

    # make sure the configuration is not readable for all users
    chmod 640 helfertool/settings.py

    # update dependencies
    pip install -r requirements.txt
    python manage.py bower install

    # install migrations
    python manage.py migrate

    # update static files
    python manage.py collectstatic --noinput

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
