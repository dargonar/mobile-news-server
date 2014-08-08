#!/bin/sh
# Parametro version vacio?
if [[ "$1" == "" ]]; then
  echo "uso: 'cron [on|off]'"
  exit
fi

ORG=cron-off.yaml
if [[ "$1" == "on" ]]; then
  ORG=cron-on.yaml
fi

cp appengine/$ORG appengine/cron.yaml

# Upload to appengine
appcfg.py --oauth2 --no_cookies update_cron appengine/.

