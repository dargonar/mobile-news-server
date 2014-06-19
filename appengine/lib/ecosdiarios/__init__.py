# -*- coding: utf-8 -*-
import logging
import re

from bs4 import BeautifulSoup
from collections import OrderedDict
from datetime import datetime
from utils import months, date_add_str, read_clean, clean_content, multi_fetch, date2iso
from xmlbuild import XMLBuild

conf = {  'title'       : u'ECOSDIARIOS',
          'url'         : u'http://www.ecosdiariosweb.com.ar',
          'description' : u'ECOSDIARIOS',
          'copyright'   : u'2013 ECOSDIARIOS',
          'logo'        : u'http://www.ecosdiariosweb.com.ar/templates/gavick_news_portal/images/np_logo.png' }

main_url = 'http://www.ecosdiariosweb.com.ar/'

def fullimg(url):
  if url is None:
    return url

  if url.startswith('/'):
    url = main_url[:-1] + url

  return url

def get_guid(href):
  return re.compile('\d+').findall(href)[-1]

  guid = href.split('_')[0] 
  if 'http://' in href:
    matches = re.compile('.ar/(.+)_').findall(href)
    guid = '#'
    if len(matches)>0:
      guid      = matches[0]
  return guid

# Necochea, viernes 16 de agosto 2013
def get_header_date(strdate):
  parts   = filter(lambda a: a != 'de', strdate.split())[2:]
  inx     = months.index(parts[2].lower())
  hour    = int(parts[5].split(':')[0]) 
  minute  = int(parts[5].split(':')[1]) 
  return datetime(day=int(parts[1]), month=inx+1, year=int(parts[3]), hour=hour, minute=minute)

# viernes 16 de agosto 2013
def get_funebre_date(strdate):
  parts = filter(lambda a: a != 'de', strdate.split())[1:]
  inx = months.index(parts[1].lower())
  return datetime(int(parts[2]), inx+1, int(parts[0]))

# Viernes, 16 de Agosto de 2013 11:53
def get_section_date(strdate):
  parts = filter(lambda a: a != 'de', strdate.split())[1:]
  inx = months.index(parts[1].lower())
  hhmm = parts[-1].split(':')
  return datetime(int(parts[2]), inx+1, int(parts[0]), int(hhmm[0]), int(hhmm[1]))

def rss_index(args):
  soup = BeautifulSoup(read_clean('http://www.ecosdiariosweb.com.ar/', use_cache=False, encoding='iso-8859-1'))
  today_date = get_header_date(soup.select('div.cabecera div.logo div.fecha p')[-1].text)

  builder = XMLBuild(conf, today_date)

  # las del scroll de fotos
  tmp = soup.select('div.wrap div.contenedor div.col3 div.col1  div.w620 div.nota.notafinal div.slide620 div.scrollable620 a')
  for i in xrange(len(tmp)): 
    a = tmp[i]
    item = {}
    item['title']     = a.find_all('div',attrs={'class':'titularslide620'})[0].text.strip()
    item['link']      = '%s%s' % (main_url, a['href'])
    item['guid']      = get_guid(a['href'])
    item['category']  = 'Portada'
    item['thumbnail'] = fullimg(a.img['src'] if a.img is not None else None) #('%s/%s' % (main_url, a.img['src'])) if len(p) > 1 and p[0].img is not None else None
    item['subheader'] = None
    builder.add_item(item)
  
  tmp = soup.select('div.wrap div.contenedor div.col3 div.col1  div.w620 div.noticias3 div.w193')
  for i in xrange(len(tmp)): 
    img = tmp[i].find_all('div',attrs={'class':'fotoNota'})[0].a.img
    a = tmp[i].find_all('h3')[0].a
    category = 'Portada'
    if '/notas-de-opinion/' in a['href'] or '/el-comentario/' in a['href']:
      category = u'Opinión'
    else:
      if '/arte-espectaculos/' in a['href']:
        category = u'Arte y Espectáculos'
    
    item = {}
    item['title']     = a.text.strip()
    item['link']      = '%s%s' % (main_url, a['href'])
    item['guid']      = get_guid(a['href'])
    item['category']  = category
    item['thumbnail'] = fullimg(img['src'] if img is not None else None) #('%s/%s' % (main_url, a.img['src'])) if len(p) > 1 and p[0].img is not None else None
    item['subheader'] = None
    builder.add_item(item)

  tmp = soup.select('div.wrap div.contenedor div.col3 div.col1 div.w620 div.nota div.modulo_seccion div.box div.f-left')
  for i in xrange(len(tmp)): 
    img         = tmp[i].find_all('div',attrs={'class':'fotoNota'})[0].a.img
    a           = tmp[i].find_all('h6')[0].a
    subbheader  = tmp[i].find_all('p')[0].text.strip()
    item = {}
    item['title']     = a.text.strip()
    item['link']      = '%s%s' % (main_url, a['href'])
    item['guid']      = get_guid(a['href'])
    item['category']  = 'Deportes'
    item['thumbnail'] = fullimg(img['src'] if img is not None else None) #('%s/%s' % (main_url, a.img['src'])) if len(p) > 1 and p[0].img is not None else None
    item['subheader'] = subbheader
    builder.add_item(item)

  tmp = soup.select('div.wrap div.contenedor div.col3 div.col1 div.w620 div.cont_video620 div.videos620_thumb li')
  for i in xrange(len(tmp)): 
    a           = tmp[i].a
    img         = a.find_all('img')[0] if len(a.find_all('img'))>0 else None
    title       = a.find_all('div',attrs={'class':'tit'})[0].text.strip()
    item = {}
    item['title']     = title
    item['link']      = '%s%s' % (main_url, a['href'])
    item['guid']      = get_guid(a['href'])
    item['category']  = u'Galería de videos'
    item['thumbnail'] = fullimg(img['src'] if img is not None else None) #('%s/%s' % (main_url, a.img['src'])) if len(p) > 1 and p[0].img is not None else None
    item['subheader'] = None
    builder.add_item(item)

  # tmp = soup.select('div.wrap div.contenedor div.col3 div.col1 div.w620 div.slide620_4noticias div.scrollable620 a')
  # for i in xrange(len(tmp)): 
  #   a           = tmp[i]
  #   img         = a.find_all('img')[0] if len(a.find_all('img'))>0 else None
  #   title       = a.find_all('strong')[0].text.strip()
  #   item = {}
  #   item['title']     = title
  #   item['link']      = '%s/%s' % (main_url, a['href'])
  #   item['guid']      = get_guid(a['href'])
  #   item['category']  = u'Fotoreportajes'
  #   item['thumbnail'] = img['src'] if img is not None else None #('%s/%s' % (main_url, a.img['src'])) if len(p) > 1 and p[0].img is not None else None
  #   item['subheader'] = None
  #   builder.add_item(item)

  tmp = soup.select('div.wrap div.contenedor div.col3 div.col2 div.nota300')
  for i in xrange(len(tmp)): 
    category    = tmp[i].find_all('div',attrs={'class':'cabezal'})
    notas       = tmp[i].find_all('div',attrs={'class':'f-left'})
    
    if len(category)==0 or len(notas)==0:
      if len(category)>0 and len(tmp[i].find_all('div',attrs={'class':'notafinal'}))>0:
        category_txt  = category[0].text.strip() 
        img           = tmp[i].find_all('div',attrs={'class':'fotoNota'})[0].a.img
        a             = tmp[i].find_all('p')[0].a
        item = {}
        item['title']     = a.text.strip()
        item['link']      = '%s%s' % (main_url, a['href'])
        item['guid']      = get_guid(a['href'])
        item['category']  = category_txt
        item['thumbnail'] = fullimg(img['src'] if img is not None else None) #('%s/%s' % (main_url, a.img['src'])) if len(p) > 1 and p[0].img is not None else None

        item['subheader'] = None
        builder.add_item(item)

      else:
        continue

    category_txt  = category[0].text.strip() 
    
    for x in xrange(len(notas)):
      img         = notas[x].find_all('div',attrs={'class':'fotoNota'})[0].a.img
      a           = notas[x].find_all('h6')[0].a
      
      item = {}
      item['title']     = a.text.strip()
      item['link']      = '%s%s' % (main_url, a['href'])
      item['guid']      = get_guid(a['href'])
      item['category']  = category_txt
      item['thumbnail'] = fullimg(img['src'] if img is not None else None) #('%s/%s' % (main_url, a.img['src'])) if len(p) > 1 and p[0].img is not None else None
      item['subheader'] = None
      builder.add_item(item)
  return builder.get_value()

  # tmp = soup.select('table.blog table.contentpaneopen')
  # for i in xrange(len(tmp)/2): 
  #   head, body = tmp[2*i], tmp[2*i+1]
    
  #   # Blank notice
  #   if head.tr.a is None:
  #     continue

  #   p = body.find_all('p')

  #   item = {}
  #   item['title']     = head.tr.a.text.strip()
  #   item['link']      = '%s/%s' % (main_url, head.tr.a['href'])
  #   item['guid']      = re.compile('&id=(\d+)').findall(item['link'])[0]
  #   item['category']  = body.tr.td.span.text.strip()
  #   item['thumbnail'] = ('%s/%s' % (main_url, p[0].img['src'])) if len(p) > 1 and p[0].img is not None else None
  #   item['subheader'] = p[-1].text
  #   builder.add_item(item)

  return builder.get_value()

def rss_menu(args):
  
  soup = BeautifulSoup(read_clean('http://www.ecosdiariosweb.com.ar/', use_cache=False, encoding='iso-8859-1'))
  today_date = get_header_date(soup.select('div.cabecera div.logo div.fecha p')[-1].text)

  builder = XMLBuild(conf, today_date)

  for n in soup.select('div.cabecera div.contenedor div.cont-menu ul.menu')[0].find_all('li'):
    if n.a['href'] is None or len(n.a['href'])==0:
      if n.a.text.strip().lower() == 'servicios':
        break
      continue
    item = {}
    item['title']     = n.a.text.strip().capitalize() #title() #upper()
    item['link']      = n.a['href'].strip().replace('/', '')
    item['guid']      = n.a['href'].strip().replace('/', '')
    item['pubDate']   = today_date
    
    builder.add_section(item)

  return builder.get_value()

def rss_section(args):

  soup = BeautifulSoup(read_clean('%s%s/' % (main_url, args['host']), use_cache=False, encoding='iso-8859-1'))
  today_date = get_header_date(soup.select('div.cabecera div.logo div.fecha p')[-1].text)
  
  builder = XMLBuild(conf, today_date)

  category = ''
  for n in soup.select('div.cabecera div.contenedor div.cont-menu ul.menu')[0].find_all('li'):
    if n.a['href'].replace('/', '') == args['host']:
      category = n.a.text.strip().capitalize()
      break

  tmp = soup.select('div.wrap div.contenedor div.seccion div.col3 div.col1 div.nota620_apaisada')
  for i in xrange(len(tmp)): 
    img         = tmp[i].find_all('div',attrs={'class':'fotoNota'})[0].a.img
    volanta     = tmp[i].find_all('div',attrs={'class':'volanta'})[0].text.strip()
    a           = tmp[i].find_all('h5')[0].a
    subbheader  = tmp[i].find_all('p')[0].text.strip()

    item = {}
    item['title']       = a.text.strip()
    item['link']        = '%s%s' % (main_url, a['href'])
    item['guid']        = get_guid(a['href'])
    item['category']    = volanta.capitalize()
    item['description'] = category
    item['thumbnail']   = img['src'] if img is not None else None #('%s/%s' % (main_url, a.img['src'])) if len(p) > 1 and p[0].img is not None else None
    item['subheader']   = subbheader
    builder.add_item(item)

  return builder.get_value()

def rss_noticia(args):

  #full_url = 'http://www.ecosdiariosweb.com.ar/%s' % args['host']
  full_url = 'http://www.ecosdiariosweb.com.ar/la-ciudad/1/1/1/pepe-%s.html' % args['host'] 

  soup = BeautifulSoup(read_clean(full_url, use_cache=False, encoding='iso-8859-1'))
  today_date = get_header_date(soup.select('div.cabecera div.logo div.fecha p')[-1].text)

  builder = XMLBuild(conf, today_date)

  tmp = soup.select('div.wrap div.contenedor div.seccion div.col3 div.col1 div.notaint')

  if len(tmp)==0 and 'videos/' in args['host']:
    # estamos en video
    tmp = soup.select('div.wrap div.contenedor div.seccion div.col3 div.col1 div.video-grande')
    video_url = tmp[0].find_all('iframe')[0]['src']
    title = tmp[0].find_all('div', attrs={'class','bajada'})[0].text.strip()

    item = {}
    item['category']  = u'Galería de videos'
    #item['subheader'] = tmp[0].h3.text.strip()
    item['title']     = title
    item['link']      = full_url
    item['guid']      = args['host']
    item['thumbnail'] = 'http://img.youtube.com/vi/%s/0.jpg' % video_url.split('/')[-1:]
    item['video']     = video_url
    item['pubDate']   = today_date
    
    builder.add_item(item)
    return builder.get_value()
  
  content       = u''
  content_divs  = tmp[0].find_all('div',attrs={'id':'noticiaint'})[0]
  extracted_img = content_divs.find_all('div',attrs={'class':'w300'})[0].extract()
  for div in content_divs.find_all('div'):
    content = content + div.__repr__().decode('utf-8')
  
  #content = re.compile(r'<img.*?/>').sub('', content)

  img_div = extracted_img.find_all('img', attrs={'itemprop':'image'}) #tmp[0].find_all('div', attrs={'class':'fotoNota-ext'})[0]
  
  volanta = tmp[0].find_all('div',attrs={'class':'volanta'})

  item = {}
  item['lead']      = volanta[0].text.strip() if volanta and len(volanta) else None
  item['category']  = volanta[0].text.strip().capitalize() if volanta and len(volanta) else None
  item['subheader'] = tmp[0].h3.text.strip()
  item['title']     = tmp[0].h1.text.strip()
  item['link']      = full_url
  item['guid']      = args['host'] #('%s/%s' % (main_url, img_div[0]['src'])) if img_div and img_div[0] else None
  item['thumbnail'] = ('%s%s' % (main_url, img_div[0]['src'])) if img_div and img_div[0] else None
  item['pubDate']   = today_date
  item['content']   = content
  
  builder.add_item(item)
  return builder.get_value()

def rss_funebres(args):

  full_url = u'http://www.ecosdiariosweb.com.ar/p/contenidos/funebres.html'

  soup = BeautifulSoup(read_clean(full_url, use_cache=False, encoding='iso-8859-1'))
  #today_date = get_header_date(soup.select('div#top_menu p')[-1].text)
  today_date = get_header_date(soup.select('div.cabecera div.logo div.fecha p')[-1].text)

  builder = XMLBuild(conf, today_date)

  title = u'Fúnebres %s' % today_date.strftime('%d/%m')
  content = ''
  obj = soup.select('div#noticiaint div div')[2].select('div > div > div > div > div > div > div > div > div > div > div')[5]
  while obj: 

    if obj.__repr__().decode('utf-8').replace(u'\n\r',u'').replace(u'\n',u'') == u'<div><br/></div>':
      item = {}
      item['title']       = u''
      item['description'] = content
      item['link']        = full_url
      item['guid']        = full_url #re.compile('&id=(\d+)').findall(item['link'])[0]
      item['pubDate']     = date2iso(today_date)
      item['category']    = title
      builder.add_funebre(item)  
      obj     = obj.find_next_sibling('div')
      content = ''
      continue

    content = content + obj.__repr__().decode('utf-8')
    obj     = obj.find_next_sibling('div')

  # HACK POR EL DIA (no se muestra nunca el LAST FUNEBRE)
  builder.add_funebre({})
  
  return builder.get_value()

def rss_farmacia(args):

  full_url = u'http://www.ecosdiariosweb.com.ar/p/contenidos/farmacias-de-turno.html'

  soup = BeautifulSoup(read_clean(full_url, use_cache=False, encoding='iso-8859-1'))
  today_date = get_header_date(soup.select('div.cabecera div.logo div.fecha p')[-1].text)

  builder = XMLBuild(conf, today_date)
  
  content=''
  obj = soup.select('div#noticiaint div div div div div p')[0]
  obj = obj.find_next_sibling('div')
  while obj: 
    content = content + obj.__repr__().decode('utf-8')
    obj     = obj.find_next_sibling('div')

  builder.add_raw(content)
  return builder.get_value()

def get_classifieds():
  return {}
  
def get_mapping():
  return {
    'map':
    OrderedDict([
      ('section://main' , {
        'url'    : 'X: rss_index',
        'small'  : {'pt': '1_main_list.xsl',              'ls': '1_main_list.xsl'},
        'big'    : {'pt': '1_tablet_main_list.xsl',       'ls': '1_tablet_main_list.xsl'},
      }),
      
      ('noticia://' , {
        'url'    : 'X: rss_noticia',
        'small'  : {'pt': '3_new.xsl',                    'ls': '3_new.xsl'},
        'big'    : {'pt': '3_tablet_new_global.xsl',      'ls': '3_tablet_new_global.xsl'},
      }),

      ('section://' , {
        'url'    : 'X: rss_section',
        'small'  : {'pt': '2_section_list.xsl',           'ls': '2_section_list.xsl'},
        'big'    : {'pt': '1_tablet_section_list.xsl',    'ls': '1_tablet_section_list.xsl'},
      }),

      ('menu://' , {
        'url'    : 'X: rss_menu',
        'small'  : {'pt': '4_menu.xsl',                   'ls': '4_menu.xsl'},
        'big'    : {'pt': '4_tablet_menu_secciones.xsl',  'ls': '4_tablet_menu_secciones.xsl'},
      }),

      ('funebres://' , {
        'url'    : 'X: rss_funebres',
        'small'  : {'pt': '6_funebres.xsl',               'ls': '6_funebres.xsl'},
        'big'    : {'pt': '6_tablet_funebres.xsl',        'ls': '6_tablet_funebres.xsl'},
      }),

      ('farmacia://' , {
        'url'    : 'X: rss_farmacia',
        'small'  : {'pt': '7_farmacias.xsl',        'ls': '7_farmacias.xsl'},
        'big'    : {'pt': '7_tablet_farmacias.xsl', 'ls': '7_tablet_farmacias.xsl'},
      }),

      ('menu_section://main' , {
        'url'    : 'X: rss_index',
        'small'  : None,
        'big'    : {'pt': '2_tablet_noticias_portrait_en_nota_abierta.xsl',  'ls': '2_tablet_noticias_portrait_en_nota_abierta.xsl'},
      }),

      ('ls_menu_section://main' , {
        'url'    : 'X: rss_index',
        'small'  : None,
        'big'    : {'pt': '2_tablet_noticias_landscape_en_nota_abierta.xsl',  'ls': '2_tablet_noticias_landscape_en_nota_abierta.xsl'},
      }),

      ('menu_section://' , {
        'url'    : 'X: rss_section',
        'small'  : None,
        'big'    : {'pt': '2_tablet_noticias_portrait_en_nota_abierta.xsl',  'ls': '2_tablet_noticias_portrait_en_nota_abierta.xsl'},
      }),

      ('ls_menu_section://' , {
        'url'    : 'X: rss_section',
        'small'  : None,
        'big'    : {'pt': '2_tablet_noticias_landscape_en_nota_abierta.xsl',  'ls': '2_tablet_noticias_landscape_en_nota_abierta.xsl'},
      }),
    ]),
    'extras': {
      'has_clasificados' : 'http://www.ecosdiarios.com/clasificados/clasificados.pdf',
      'has_funebres'     : 'funebres://',
      'has_farmacia'     : 'farmacia://',
      'has_cartelera'    : False,
    },
    'config': {
        'android': { 'ad_mob': '', 'google_analytics' : ['UA-32663760-4'] },
        'iphone':  { 'ad_mob': '', 'google_analytics' : ['UA-32663760-4'] },
        'ipad':    { 'ad_mob': '', 'google_analytics' : ['UA-32663760-4'] }
    }
  }
