FROM debian:buster

ARG CONTAINER_VERSION="unknown"

ENV LANG=C.UTF-8

RUN apt-get update && apt-get full-upgrade -y && \
    apt-get install -y python3 python3-pip uwsgi uwsgi-plugin-python3 \
        nginx supervisor gosu rsyslog \
        libldap2-dev libsasl2-dev libmariadb-dev-compat \
        sassc \
        texlive-latex-extra texlive-fonts-recommended texlive-lang-german && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /usr/share/doc/* && \
    # add user, some directories and fix owners
    useradd --shell /bin/bash --home-dir /helfertool --create-home helfertool --uid 1000 && \
    mkdir /data /log /helfertool/run && \
    chown -R helfertool:helfertool /data /log /helfertool/run

RUN echo $CONTAINER_VERSION > /helfertool/container_version

COPY src /helfertool/src
COPY deployment/docker/helfertool.sh /usr/local/bin/helfertool
COPY deployment/docker/uwsgi.conf /helfertool/uwsgi.conf
COPY deployment/docker/supervisord.conf /helfertool/supervisord.conf
COPY deployment/docker/nginx.conf /helfertool/nginx.conf
COPY deployment/docker/rsyslog.conf /helfertool/rsyslog.conf

RUN cd /helfertool/src/ && \
    # install python libs
    pip3 install -r requirements.txt mysqlclient uwsgitop && \
    # generate compressed CSS/JS files
    HELFERTOOL_CONFIG_FILE=/dev/null python3 manage.py compress --force && \
    # copy static files
    HELFERTOOL_CONFIG_FILE=/dev/null python3 manage.py collectstatic --noinput && \
    chmod -R go+rX /helfertool/static && \
    # fix permissions
    chmod +x /usr/local/bin/helfertool

VOLUME ["/config", "/data", "/log"]
EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/helfertool"]
CMD ["run"]
