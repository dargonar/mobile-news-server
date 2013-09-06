import feedparser
import jinja2
import email.utils

from urllib2 import urlopen
from bs4 import BeautifulSoup

env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
home_template = env.get_template('_home.html')

items = []

d = feedparser.parse('http://www.eldia.com.ar/rss/rss.aspx?ids=8')
#print len(d['items'])

for item in d['items']:

  #if len(items)>0:
  #  break

  if item.has_key('title'):
    print 'Bajando ' + item['link']
    soup = BeautifulSoup(urlopen(item['link']))

    # Bajada
    bajada = soup.select('div#baja h3')
    if len(bajada) == 0:
      bajada = soup.select('h3#baja')
    
    item['bajada'] = bajada[0].text if len(bajada) else ''

    # Contenido
    contenido = soup.select('div#texto')
    item['contenido'] = contenido[0].text if len(contenido) else ''

    # Imagen
    imagen = soup.select('div.ImagenesNoticia img.Foto')
    item['imagen'] = imagen[0].attrs['src'] if len(imagen) and 'src' in imagen[0].attrs else ''

    # Hora
    hora = email.utils.parsedate(item.published)
    item['hora'] = '%02d:%02d' % (hora[3],hora[4])

    items.append(item)

params = {'items':items}

f=open('/Users/matias/Downloads/layout_mobile_adira/m1/index-2.html', 'w')
f.write(home_template.render(**params).encode('utf-8'))
f.close()

