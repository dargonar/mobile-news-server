# -*- coding: utf-8 -*-
import logging
import re

from bs4 import BeautifulSoup
from collections import OrderedDict
from datetime import datetime, timedelta
from utils import days, months, date_add_str, read_clean, clean_content, multi_fetch, date2iso
from xmlbuild import XMLBuild

conf = {  'title'       : u'DIARIO CASTELLANOS',
          'url'         : u'http://www.diariocastellanos.net',
          'description' : u'El diario de Rafaela, Argentina - Con la verdad no ofendo ni temo',
          'copyright'   : u'2013, Editora del Centro, Propiedad Intelectual N84.363, todos los derechos reservados',
          'logo'        : u'http://www.diariocastellanos.net/images/header/castellanos.png' }


# 15 de Agosto de 2013 | 22:35 hs.
def get_noticia_date(strdate):
  parts = strdate.split()
  parts = filter(lambda a: a!='de' and a!='del',parts)
  month = parts[2].lower() if parts[1].lower()!='setiembre' else 'septiembre'
  inx = months.index(month)
  return datetime(int(parts[3]), inx+1, int(parts[1]))

def date2spanish(date):
  return '%s, %02d de %s del %d' % (days[date.weekday()].title(), date.day, months[date.month-1].title(), date.year)

def rss_index(args):

  # Puede ser la main o nos llaman de rss_section para parsear una seccion
  full_url = 'http://www.diariocastellanos.net/'
  if 'full_url' in args:
    full_url = args['full_url']

  soup = BeautifulSoup(read_clean(full_url, use_cache=False))
  today_date = datetime.now()+timedelta(hours=-3)

  builder = XMLBuild(conf, today_date)

  # Tomamos la categoria si es una "seccion"
  category = args.get('category')
  if category:
    category = soup.select('div.seccion')
    if len(category) == 0:
      return builder.get_value()
    category = category[0].text.title()

  def add_item(n, category=None):
    
    pubDate = n.find_all('div',{'class':'fecha'})

    item = {}
    item['title']     = n.find_all('div', {'class':'titulo'})[0].text.title()
    item['link']      = n.find_all('a')[-1].attrs['href']
    matches = re.compile('/noticia/(.+)').findall(item['link'])
    item['guid'] = '#'
    if len(matches)>0:
      item['guid']      = matches[0]
    
    # if len(pubDate):
    #   item['pubDate'] = date2iso(get_noticia_date(pubDate[0].text))
    
    an_img = n.find_all('img')
    logging.error('-----------------------')
    #logging.error(an_img)
    if an_img and len(an_img) > 0:
      if an_img[0]['data-original'] and len(an_img[0]['data-original']) > 0:
        an_img = an_img[0]['data-original']
      else:
        an_img = an_img[0]['src'] if an_img[0]['src']
    logging.error(an_img)
    item['category']  = category if category is not None else n.a.text.upper()
    item['thumbnail'] = an_img if an_img else None
    item['subheader'] = n.p.text if n.p else None
    builder.add_item(item)

  for n in soup.select('div.noticia-p1')+soup.select('div.noticia-p2'):
    add_item(n, category)
  
  for d in soup.select('div.seccionppal'):
    category = d.a.h1.text.title()
    for n in d.find_all('div', {'class':'noticia'}):
      add_item(n, category)


  return builder.get_value()

def rss_menu(args):
  
  soup = BeautifulSoup(read_clean('http://www.diariocastellanos.net/', use_cache=False))
  today_date = datetime.now()+timedelta(hours=-3)
  
  sections = set()

  builder = XMLBuild(conf, today_date)
  for n in soup.select('div.menu li a'):
    if n['href'] == '#': continue
    item = {}
    item['title']     = n.text.title()
    item['link']      = n['href']
    item['guid']      = item['link'][[x.start() for x in re.finditer('/', item['link'])][-2]+1:-1]
    item['pubDate']   = date_add_str(today_date, '00:00')
    
    if item['title'].lower().strip() != 'portada' and item['guid'] not in sections:
      builder.add_section(item)
      sections.add(item['guid'])

  return builder.get_value()

def rss_seccion(args):
  
  full_url = 'http://www.diariocastellanos.net/seccion/%s/' % args['host'].lower()
  logging.error('  section url ==> %s' % full_url)
  return rss_index({'full_url':full_url, 'category':True})

def rss_noticia(args):

  full_url = 'http://www.diariocastellanos.net/noticia/%s' % args['host']

  html = read_clean(full_url, clean=False, use_cache=False)
  soup = BeautifulSoup(html)
  today_date = datetime.now()+timedelta(hours=-3)

  builder = XMLBuild(conf, today_date)
  
  n = soup.select('div#main div.noticia')[0]
  content = n.find_all('div',{'class':'txt'})[0].__repr__().decode('utf-8')
  content = re.sub(r'<([a-z][a-z0-9]*)([^>])*?(/?)>', r'<\1>', content)
  
  # Sacamos thumbnail
  img = (n.find_all('div', {'class':'img'})[:1] or [None])[0]
  if img: img = img.img['src']

  # Sacamos galeria / Si hay galeria y no thumnail => la primer foto es el thumb
  # group = [tmp['src'] for tmp in soup.select('ul.ad-thumb-list img')]
  # if len(group) and img is None: img = group[0]

  item = {}
  item['title']     = n.h1.text
  item['link']      = full_url
  item['guid']      = args['host']
  category = re.compile('<h2 class="volanta" class="">(.+?)</h1>').findall(html)
  item['category']  = category[0].decode('utf-8') if len(category) else soup.select('div.seccion')[0].text.title()
  item['thumbnail'] = img
  # item['group']     = group
  # item['has_gallery'] = 'true' if len(group) > 0 else 'false'
  # item['pubDate']   = date2iso(get_noticia_date(n.time.text))
  item['subheader'] = n.find_all('h2')[-1].text
  item['content']   = content
  
  builder.add_item(item)
  return builder.get_value()


def rss_funebres(args):

  html = read_clean('http://diariocastellanos.net/funebres/', use_cache=False)
  html = '<html><body>'+html[html.rfind('<div id="content-funebres">'):]

  soup = BeautifulSoup(html)
  today_date = datetime.now()+timedelta(hours=-3)
  
  builder = XMLBuild(conf, today_date)

  item  = {}
  for div in soup.select('div#content-funebres div'):
    if div['class'][0] == 'fecha':
      if len(item): 
        item['description'] = content
        builder.add_funebre(item)
      
      tmp = get_noticia_date(div.text)
      item  = {}
      item['title']     = date2spanish(tmp)
      item['link']      = 'http://www.diariocastellanos.net/funebres/' 
      item['guid']      = 'no_guid'
      item['pubDate']   = tmp.strftime("%a, %d %b %Y %H:%M:%S")
      item['category']  = item['title']
      content = ''

    elif div['class'][0] == 'tipo':
      content += '<p><h1>%s</h1></p><br/>' % div.text
    elif div['class'][0] == 'titulo':
      content += '<b>%s</b></br>' % div.text
    elif div['class'][0] == 'texto':
      content += '<p>%s</p></br>' % div.text

  if len(item): 
    item['description'] = content
    builder.add_funebre(item)
  
  # HACK POR EL DIA (no se muestra nunca el LAST FUNEBRE)
  builder.add_funebre({})
  
  return builder.get_value()


#
# TEMPLATES MAPPING
#

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
        'url'    : 'X: rss_seccion',
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
        'url'    : 'X: rss_seccion',
        'small'  : None,
        'big'    : {'pt': '2_tablet_noticias_portrait_en_nota_abierta.xsl',  'ls': '2_tablet_noticias_portrait_en_nota_abierta.xsl'},
      }),

      ('ls_menu_section://' , {
        'url'    : 'X: rss_seccion',
        'small'  : None,
        'big'    : {'pt': '2_tablet_noticias_landscape_en_nota_abierta.xsl',  'ls': '2_tablet_noticias_landscape_en_nota_abierta.xsl'},
      }),
    ]),
    'extras': {
      'has_clasificados' : False,
      'has_funebres'     : 'funebres://',
      'has_farmacia'     : 'http://circulorafaela.com.ar/farmacias.htm',
      'has_cartelera'    : 'http://www.rafaela.gov.ar/cine/',
    },
    'config': {
        'android': { 'ad_mob': '', 'google_analytics' : ['UA-32663760-3'] },
        'iphone':  { 'ad_mob': '', 'google_analytics' : ['UA-32663760-3'] },
        'ipad':    { 'ad_mob': '', 'google_analytics' : ['UA-32663760-3'] }
    }
  } 