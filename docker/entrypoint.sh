#!/bin/sh -eu

export MUSL_LOCPATH=/usr/share/i18n/locales/musl
cd /bot
. ./.env
exec python3 main.py
