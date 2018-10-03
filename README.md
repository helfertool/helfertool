Helfertool is a Python3 and Django based tool that allows to manage the
volunteers or staff for an event.

See <https://www.helfertool.org> for more information.

# Install

Please have a look at the
[admin guide](https://docs.helfertool.org/admin/index.html)
in our documentation.

# Environment for development

A Python virtual environment should be used for development, the necessary
Python libraries are listed in ``src/requirements.txt``.

## Runserver

Start the webserver for development:

    cd src
    python manage.py runserver

Now visit http://localhost:8000 with your browser.


## Celery and RabbitMQ

When working on a part of the Helfertool that uses Celery, a RabbitMQ instance
needs to be started:

RabbitMQ can be installed using Docker (note: the RabbitMQ server listens
on port 5672 to every incoming connection, you should configure a firewall):

    docker run -d --rm --hostname helfertool-rabbitmq --name helfertool-rabbitmq \
        -p 5672:5672 rabbitmq

The default settings in ``helfertool.yaml`` do not need to be changed.

Now start celery:

    celery -A helfertool worker -c 2 --loglevel=info

## Mails

The Helfertool tries to send mails to localhost:25 with the default
configuration.

If you want to test the E-Mail part during development, you can start a
SMTP debug server using this command:

    python -m smtpd -n -c DebuggingServer localhost:1025

Additionally set the SMTP port to 1025 in ``helfertool.yaml``:

The advantage of this method compared to the console backend from Django is,
that you also see the mails sent in Celery tasks in the same window.

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
