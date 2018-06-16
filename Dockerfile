FROM python:3.6

RUN apt-get update && \
    apt-get install -y nginx uwsgi uwsgi-plugin-python3 libldap2-dev libsasl2-dev && \
    # texlive-latex-extra texlive-fonts-recommended texlive-lang-german
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir /data && \
    useradd --shell /bin/bash --home-dir /helfertool --create-home helfertool

COPY src /helfertool/src
COPY deployment/docker/start-helfertool.sh /helfertool/start.sh

RUN rm /etc/nginx/sites-enabled/default && \
    # link settings
    cd /helfertool/src/ && \
    ln -s /data/settings_local.py helfertool/settings_local.py && \
    # install python libs
    pip3 install -r requirements.txt && \
    pip3 install mysqlclient psycopg2-binary && \
    # copy static files
    mkdir /helfertool/static/ && \
    python3 manage.py collectstatic --noinput && \
    # fix permissions
    chown -R helfertool:helfertool /helfertool /data && \
    chmod +x /helfertool/start.sh

USER helfertool

VOLUME ["/data"]
EXPOSE 1234

ENTRYPOINT ["/helfertool/start.sh"]
