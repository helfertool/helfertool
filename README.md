# Install

It is recommended to use virtualenv:

    virtualenv helfertool
    cd helfertool
    . ./bin/activate

    git clone git@gitlab.fs.tum.de:hertle/helfertool.git

## Dependencies

### Software

 * Python 2 or 3
 * pdflatex (from TeX Live)

### Python modules

 * Django 1.8
 * django-modeltranslation
 * django-bootstrap3
 * django-bleach
 * XlsxWriter
 * Pillow
 * reportlab
 * sphinx (only to build the documentation)
 * locustio (only for load test, Python 2 only at the moment)

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

By default Django uses a SQLite database that can be generated using the
following command inside the project directory:

    python manage.py migrate

Then a superuser should be created:

    python manage.py createsuperuser

Now you can start the webserver for development:

    python manage.py runserver

Now visit http://localhost:8000 with your browser.

## Deployment

There are a lot of possibilities to deploy a Django project. For
helfen.fs.tum.de Apache2, uWSGI and MySQL are used. See here for the webserver
part: https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/uwsgi/

Instead of installing uwsgi with pip we used the Debian repository.


# Command line interface

In addition to the CLI of Django this software provides these commands:

## openregistration

    python manage.py openregistration test

*test* is the URL name.

## closeregistration

    python manage.py closeregistration test

*test* is the URL name.

## Using at to open the registration

    at '13:55 10/18/2015'
