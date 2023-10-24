FROM debian:bookworm

ARG CONTAINER_VERSION="unknown"

ENV LANG=C.UTF-8
ENV DJANGO_SETTINGS_MODULE="helfertool.settings_container"
ENV HELFERTOOL_CONFIG_FILE="/config/helfertool.yaml"

RUN apt-get update && apt-get full-upgrade -y && \
    apt-get install --no-install-recommends -y \
        supervisor nginx rsyslog pwgen curl \
        python3 python3-venv python3-dev uwsgi uwsgi-plugin-python3 \
        build-essential pkg-config ldap-utils libldap2-dev libsasl2-dev libmariadb-dev libpq-dev libmagic1 \
        texlive-latex-extra texlive-plain-generic texlive-fonts-recommended texlive-lang-german && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /usr/share/doc/* && \
    # add user, some directories and set file permissions
    useradd --shell /bin/bash --home-dir /helfertool --create-home helfertool --uid 10001 && \
    mkdir -p /config /data /log /helfertool/run && \
    chown -R helfertool:helfertool /config /data /log && \
    chmod -R 0777 /helfertool/run && \
    # nginx always writes to /var/log/nginx/error.log before reading the config
    # so we redirect it to a writable location
    rm /var/log/nginx/error.log && \
    ln -s /helfertool/run/nginx/error.log /var/log/nginx/error.log && \
    # we should have a writable /tmp, some tools expect this
    rm -rf /tmp && \
    ln -s /helfertool/run/tmp /tmp

COPY src /helfertool/src
COPY deployment/container/etc /helfertool/etc
COPY deployment/container/helfertool.sh /usr/local/bin/helfertool
COPY deployment/container/healthcheck.sh /usr/local/bin/healthcheck

RUN echo $CONTAINER_VERSION > /helfertool/container_version && \
    # install python libs
    cd /helfertool/src/ && \
    python3 -m venv /helfertool/venv/ && \
    /helfertool/venv/bin/pip install wheel -r requirements.txt -r requirements_prod.txt && \
    rm -rf /root/.cache/pip/ && \
    # generate compressed CSS/JS files
    HELFERTOOL_CONFIG_FILE=/dev/null /helfertool/venv/bin/python manage.py compress --force && \
    # copy static files
    HELFERTOOL_CONFIG_FILE=/dev/null /helfertool/venv/bin/python manage.py collectstatic --noinput && \
    chmod -R go+rX /helfertool/static && \
    # fix permissions
    chmod +x /usr/local/bin/helfertool /usr/local/bin/healthcheck

VOLUME ["/config", "/data", "/log", "/helfertool/run"]
EXPOSE 8000

USER helfertool
ENTRYPOINT ["/usr/local/bin/helfertool"]
CMD ["run"]

HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 CMD ["/usr/local/bin/healthcheck"]
