FROM debian:stretch

RUN apt-get update && \
    apt-get install -y python3 python3-pip uwsgi uwsgi-plugin-python3 nginx supervisor libldap2-dev libsasl2-dev libmariadbclient-dev && \
    # texlive-latex-extra texlive-fonts-recommended texlive-lang-german
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir /data && \
    useradd --shell /bin/bash --home-dir /helfertool --create-home helfertool

COPY src /helfertool/src
COPY deployment/docker/start-helfertool.sh /helfertool/start.sh
COPY deployment/docker/uwsgi.conf /helfertool/uwsgi.conf
COPY deployment/docker/supervisord.conf /helfertool/supervisord.conf
COPY deployment/docker/nginx.conf /helfertool/nginx.conf

RUN cd /helfertool/src/ && \
    # install python libs
    pip3 install -r requirements.txt mysqlclient psycopg2-binary && \
    # copy static files
    HELFERTOOL_CONFIG_FILE=/dev/null python3 manage.py collectstatic --noinput && \
    # fix permissions
    chown -R helfertool:helfertool /helfertool /data /var/lib/nginx /var/log/nginx /usr/share/nginx && \
    chmod +x /helfertool/start.sh

USER helfertool

VOLUME ["/data"]
EXPOSE 8000

ENTRYPOINT ["/helfertool/start.sh"]
