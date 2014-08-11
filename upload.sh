#!/bin/sh

# Parametro version vacio?
if [[ "$1" == "" ]]; then
  echo "uso: 'upload version'"
  exit
fi

ver=$1

echo "generating version $ver ...."

# Cambiamos la linea que tiene la version del app.yaml
cat appengine/app.yaml | sed 's/^version: \(.*\)$/version: '$ver'/g' > app.yaml.tmp
mv app.yaml.tmp appengine/app.yaml

# Compilamos los templates jinja2
/c/Python27/python.exe compile_templates.py

# Upload to appengine
appcfg.py --oauth2 --no_cookies update appengine/.

