#!/bin/sh

# Parametro version vacio?
if [[ "$1" == "" ]]; then
  echo "uso: 'to_version.sh version'"
  exit
fi

# Cambiamos la linea que tiene la version del app.yaml
cat appengine/app.yaml | sed 's/^version: \(.*\)$/version: '$1'/g' > app.yaml.tmp
mv app.yaml.tmp appengine/app.yaml

# Borramos los CSS (min) y JS (min) viejos
#git rm -f appengine/static/css/backend.min-*.css
#git rm -f appengine/static/js/backend.min-*.js

#git rm -f appengine/static/css/frontend.min-*.css
#git rm -f appengine/static/js/frontend.min-*.js

#git rm -f appengine/static_realestate/css/realestate.min-*.css
#git rm -f appengine/static_realestate/js/realestate.min-*.js

# Corremos el compresor de CSS y JS para backend
# /c/Python26/python.exe yuicompress/compress.py $1 be

# Corremos el compresor de CSS y JS para frontend
# /c/Python26/python.exe yuicompress/compress.py $1 fe

# Corremos el compresor de CSS y JS para realestate
# /c/Python26/python.exe yuicompress/compress.py $1 re

# Copiamos los min JS y min CSS a sus folders
# mv backend.min-$1.js appengine/static/js
# git add appengine/static/js/backend.min-$1.js

# mv backend.min-$1.css appengine/static/css
# git add appengine/static/css/backend.min-$1.css

# mv frontend.min-$1.js appengine/static/js
# git add appengine/static/js/frontend.min-$1.js 

# mv frontend.min-$1.css appengine/static/css
# git add appengine/static/css/frontend.min-$1.css

# mv realestate.min-$1.js appengine/static_realestate/js
# git add appengine/static_realestate/js/realestate.min-$1.js 

# mv realestate.min-$1.css appengine/static_realestate/css
# git add appengine/static_realestate/css/realestate.min-$1.css

# Compilamos los templates jinja2
/c/Python27/python.exe compile_templates.py
