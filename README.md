Helfertool is a Python3 and Django based tool that allows to manage the
volunteers or staff for an event.

See <https://www.helfertool.org> for more information.

# Install

Please have a look at the
[deployment guide](https://docs.helfertool.org/deploy/index.html)
in our documentation.

# Environment for development

Most of the steps are described in the
[deployment guide](https://docs.helfertool.org/deploy/index.html),
you can skip the installation and configuration of a webserver.

There are some differences to the deployment guide that should make life
easier for you:

## Celery

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

The advantage of this method compared to the console backend from Django is,
that you also see the mails sent in Celery tasks in the same window.

## Runserver

Start the webserver for development:

    python manage.py runserver

Now visit http://localhost:8000 with your browser.

# LICENSE

Copyright (C) 2018  Sven Hertle

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
