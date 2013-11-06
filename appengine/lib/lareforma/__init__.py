# -*- coding: utf-8 -*-
import logging
import re
import threading

from bs4 import BeautifulSoup
from collections import OrderedDict
from datetime import datetime, timedelta
from utils import days, months, date_add_str, read_clean, clean_content, multi_fetch, date2iso
from xmlbuild import XMLBuild

conf = {  'title'       : u'DIARIO LA REFORMA',
          'url'         : u'http://www.diariolareforma.com.ar/',
          'description' : u'Diario La Reforma - El diario de la Pampa',
          'copyright'   : u'LA REFORMA S.R.L. - Copyright 2012',
          'logo'        : u'http://www.diariolareforma.com.ar/2013/wp-content/themes/lareforma/images/logo.png' }


# GENERAL | 15/10/2013
def get_header_date(strdate):
  parts = strdate.split('|')[1].strip().split('/')
  return datetime(year=int(parts[2]), month=int(parts[1]), day=int(parts[0]))

# GENERAL | 15/10/2013 ??
def get_noticia_date(strdate):
  hh, mm = strdate.split('|')[1].strip().split()[0].split(':')
  parts = strdate.split()
  parts = parts[0:parts.index('|')]
  parts = filter(lambda a: a!='de',parts)
  month = parts[1].lower() if parts[1].lower()!='setiembre' else 'septiembre'
  inx = months.index(month)
  return datetime(int(parts[2]), inx+1, int(parts[0]), int(hh), int(mm))

def get_index_item(element, is_funebre=False):
    
    head          = element.find_all('div',{'class':'titles-cont'})[0].h3.a if not is_funebre else element.find_all('div',{'class':'titles-cont'})[0].h3
    article_date  = get_header_date(element.find_all('span',{'class':'category-fecha'})[0].text )
    if len(element.find_all('div',{'class':'thumbNotes'}))>0:
      img_div       = element.find_all('div',{'class':'thumbNotes'})[0]
    else:
      img_div = None
    sub_h         = element.find_all('div',{'class':'extract'})[0]
    
    item = {}
    item['title']     = head.text
    item['link']      = head['href'] if not is_funebre else '#'
    item['guid']      = item['link'].split('/')[-2] if not is_funebre else '?'
    # item['pubDate']   = article_date.strftime("%a, %d %b %Y %H:%M:%S") 
    item['rawDate']   = article_date
    item['category']  = element.find_all('span',{'class':'category'})[0].text
    item['thumbnail'] = img_div.a.img['src'] if img_div and img_div.a and img_div.a.img else None
    if not is_funebre:
      item['subheader'] = sub_h.p.text if sub_h.p else None
    else:
      item['description'] = sub_h.p.text if sub_h.p else None
    return item    
    
def rss_index(args):
  soup = BeautifulSoup(read_clean('http://www.diariolareforma.com.ar/', use_cache=False))
#  soup = BeautifulSoup(urlopen('http://www.diariolareforma.com.ar/', timeout=25).read())
  today_date = get_header_date(soup.select('#column1 div.box span.category-fecha')[0].text)

  builder = XMLBuild(conf, today_date)

  notas1 = soup.select('#column1 div.box')
  notas2 = soup.select('#column2 div.box')
  
  for i in xrange(max(len(notas1), len(notas2))):
    if len(notas1)>i:
      item = get_index_item(notas1[i])
      if item is not None: builder.add_item(item)    
    if len(notas2)>i:
      item = get_index_item(notas2[i])
      if item is not None: builder.add_item(item)    
    
  return builder.get_value()

def rss_menu(args):
  
  soup = BeautifulSoup(read_clean('http://www.diariolareforma.com.ar/', use_cache=False))
  today_date = get_header_date(soup.select('#column1 div.box span.category-fecha')[0].text)

  builder = XMLBuild(conf, today_date)

  for cat in soup.select('ul#suckerfishnav li'):
  
    if (u'menu-item-object-category' not in cat['class']): # and (u'menu-item-object-page' not in cat['class']):
      #logging.error(' -- NO EN CLASS' + str(cat['class']))
      continue
    if not cat.a or not cat.a.get('href'):
      # logging.error(' -- NO HAY a_link' + str(cat))
      continue
    if cat.a.text.lower() == 'principal' or cat.a.text.lower() == u'necrológicas':
      # logging.error(' -- es principal ' + str(cat))
      continue
    if cat.findParent('ul').get('id') != 'suckerfishnav':
      # logging.error(' -- NO es hijo directo' + str(cat))
      continue
    
    link = cat.a['href'] 
    guid = link[[x.start() for x in re.finditer('/', link)][-2]+1:-1]
  
    item = {}
    item['title']     = cat.a.text
    item['link']      = cat.a['href']
    item['guid']      = guid.strip()
    # item['pubDate']   = date_add_str(today_date, '00:00')
    builder.add_section(item)
  
  #Recontra hacko para columnistas
  item = {}
  item['title']     = u'COLUMNISTAS'
  item['link']      = u'#'
  item['guid']      = u'COLUMNISTAS'
  # item['pubDate']   = date_add_str(today_date, '00:00')
  builder.add_section(item)
  
  return builder.get_value()
  
def rss_seccion(args):
  
  if args['host'].lower() == u'columnistas':
    return rss_seccion_columnistas(args) # Ojo con la seccion recontra hackeada u'COLUMNISTAS'
  
  full_url = 'http://www.diariolareforma.com.ar/2013/category/%s/' % args['host'].lower()
  return rss_index({'full_url':full_url, 'category':True})

def rss_seccion_columnistas(args):

  soup = BeautifulSoup(read_clean('http://www.diariolareforma.com.ar/', use_cache=False))
  today_date = get_header_date(soup.select('#column1 div.box span.category-fecha')[0].text)

  builder = XMLBuild(conf, today_date)

  # Obtenemos las url funebres
  urls = {}
  for cat in soup.select('ul#suckerfishnav li ul li a'):
    if cat.findParent('li').findParent('li').a.text.lower().strip() != 'columnistas':
      continue
    urls[cat['href']] = None
  
  funlock  = threading.Lock()
  items = []
  
  def handle_result(rpc, url):
    result = rpc.get_result()
    if result.status_code == 200: 
      
      soup = BeautifulSoup(clean_content(result.content))
      
      for n in soup.select('#column1 div.box'):
        item = get_index_item(n)
        with funlock:
          items.append(item)

  # Traemos en paralelo (primeras 4)
  multi_fetch(urls.keys()[:8], handle_result)
  
  builder = XMLBuild(conf, today_date)
  for item in sorted(items, key=lambda x: x['rawDate'], reverse=False):
    builder.add_item(item)
  
  return builder.get_value()
  
def rss_noticia(args): 

  full_url = 'http://www.diariolareforma.com.ar/2013/%s/' % args['host']
  # httpurl=u'http://www.diariolareforma.com.ar/2013/activistas-suspenden-la-audiencia-concedida-a-hernan-perez-orsi/'
  # soup = BeautifulSoup(urlopen(httpurl, timeout=25).read())
  soup = BeautifulSoup(read_clean(full_url, use_cache=False))
  today_date = datetime.now()+timedelta(hours=-3)

  builder = XMLBuild(conf, today_date)
 
  body = soup.select('div#content-post')[0]
 
  divimg = body.find_all('div',{'class':'foto-gallery'})
  
  content = body.find_all('div',{'class':'content-post-text'})[0]
  del content['class']
      
  item = {}
  item['title']     = body.h1.text
  item['category']  = body.find_all('span',{'class':'category'})[0].li.a.text
  item['link']      = full_url
  item['guid']      = args['host']
  item['thumbnail'] = divimg[0].a.img['src'] if len(divimg)>0 and divimg[0].a else None
  #item['pubDate']   = date2iso(today_date)
  item['content']   = content.__repr__().decode('utf-8')
  
  builder.add_item(item)
  return builder.get_value()

def rss_funebres(args):

  soup = BeautifulSoup(read_clean('http://www.diariolareforma.com.ar/2013/category/necrologicas/', use_cache=False))
  today_date = get_header_date(soup.select('#column1 div.box span.category-fecha')[0].text)

  builder = XMLBuild(conf, today_date)
  
  notas1 = soup.select('#column1 div.box')
  notas2 = soup.select('#column2 div.box')
  
  for i in xrange(max(len(notas1), len(notas2))):
    if len(notas1)>i:
      item = get_index_item(notas1[i], is_funebre=True)
      if item is not None: builder.add_funebre(item)    
    if len(notas2)>i:
      item = get_index_item(notas2[i], is_funebre=True)
      if item is not None: builder.add_funebre(item)    
  
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
      'has_farmacia'     : False,
      'has_cartelera'    : 'http://cinegranpampa.com.ar/',
    },
    'config': {
        'android': { 'ad_mob': '', 'google_analytics' : ['UA-32663760-7'] },
        'iphone':  { 'ad_mob': '', 'google_analytics' : ['UA-32663760-7'] },
        'ipad':    { 'ad_mob': '', 'google_analytics' : ['UA-32663760-7'] }
    }
  } 