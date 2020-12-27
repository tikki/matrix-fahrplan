FROM docker.io/library/alpine:latest

ENV TIMEZONE="Europe/Berlin"

RUN apk upgrade --no-cache \
    && apk add --virtual build-deps --no-cache \
        python3-dev \
        gcc \
        openssl-dev \
        musl-dev \
        olm-dev \
    && apk add --no-cache \
        python3 \
        py3-pip \
        py3-cffi \
        openssl \
        musl \
        musl-locales \
        olm \
        tzdata \
    && echo "$TIMEZONE" >/etc/timezone \
    && cp /usr/share/zoneinfo/"$TIMEZONE" /etc/localtime \
    && pip install -U pip 'matrix-nio[e2e]' \
    && apk del --rdepends build-deps tzdata \
    && rm -rf /root/.cache

COPY requirements.txt /
RUN pip install -Ur /requirements.txt

COPY entrypoint.sh /

VOLUME ["/bot"]
VOLUME ["/data"]

CMD ["/entrypoint.sh"]
