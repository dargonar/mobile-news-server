# -*- coding: utf-8 -*-

import logging
import re

from bs4 import BeautifulSoup
from collections import OrderedDict
from datetime import datetime
from utils import months, date_add_str, read_clean, clean_content, multi_fetch, date2iso
from xmlbuild import XMLBuild

conf = {  'title'       : u'PREGON',
          'url'         : u'http://www.pregon.com.ar/',
          'description' : u'El diario de Jujuy',
          'copyright'   : u'Todos los Derechos Registrados - Pregon Jujuy- San Salvador de Jujuy - Argentina Año 2001',
          'logo'        : u'http://www.pregon.com.ar/img/LOGOPREGON.png' }

main_url = 'http://www.pregon.com.ar/'

# Viernes 16 de Agosto de 2013
def get_header_date(strdate):
  parts = filter(lambda a: a!='de',strdate.split()[1:])
  inx = months.index(parts[1].lower())
  return datetime(int(parts[2]), inx+1, int(parts[0]))

# 15 de Agosto de 2013 | 22:35 hs.
def get_noticia_date(strdate):
  hh, mm = strdate.split('|')[1].strip().split()[0].split(':')
  parts = strdate.split()
  parts = parts[0:parts.index('|')]
  parts = filter(lambda a: a!='de',parts)
  month = parts[1].lower() if parts[1].lower()!='setiembre' else 'septiembre'
  inx = months.index(month)
  return datetime(int(parts[2]), inx+1, int(parts[0]), int(hh), int(mm))

def rss_index(args):
  soup = BeautifulSoup(read_clean('http://www.pregon.com.ar/', use_cache=False))
  today_date = get_header_date(soup.select('div.clima div')[-1].text)

  builder = XMLBuild(conf, today_date)

  for main in soup.select('div.destacadasbox100')+soup.select('div.destacadasbox50'):
    item = {}
    item['title']     = main.h1.text
    item['link']      = main.a['href']
    item['guid']      = re.compile('\d+').findall(item['link'])[0]
    item['thumbnail'] = main.img['src'] if main.img else None
    item['subheader'] = main.p.text if main.p is not None else main.find_all('div', {'class':'box50-bajada'})[0].text
    builder.add_item(item)

  headers = soup.select('div.C1 h1 a') + soup.select('div.C2 h1 a')
  bodies  = soup.select('div.C1 div.box') + soup.select('div.C2 div.box')
  
  for i in xrange(len(headers)):
    head, body = headers[i], bodies[i]

    spans = body.p.find_all('span')

    item = {}
    item['title']     = head.text
    item['link']      = head['href']
    item['guid']      = re.compile('\d+').findall(item['link'])[0]
    item['pubDate']   = date_add_str(today_date, spans[0].strong.text)
    item['thumbnail'] = body.div.img['src'] if body.div.img else None
    item['subheader'] = spans[1].text
    builder.add_item(item)    
    
  return builder.get_value()

def rss_menu(args):
  
  soup = BeautifulSoup(read_clean('http://www.pregon.com.ar/', use_cache=False))
  today_date = get_header_date(soup.select('div.clima div')[-1].text)

  builder = XMLBuild(conf, today_date)

  for n in soup.select('ul#menudesplegable li ul li a'):
    
    category, guid = re.compile('\d+').findall(n['href'])
    if int(category) != 4: 
      continue

    item = {}
    item['title']     = n.text
    item['link']      = n['href']
    item['guid']      = guid
    item['pubDate']   = date_add_str(today_date, '00:00')
    builder.add_section(item)

  return builder.get_value()

def rss_section(args):

  soup = BeautifulSoup(read_clean('http://www.pregon.com.ar/subseccion/4/%s/dummy.html' % args['host'], use_cache=False))
  today_date = get_header_date(soup.select('div.clima div')[-1].text)
  
  builder = XMLBuild(conf, today_date)
  category = soup.select('h1.antetituloNormal')[0].text.split()[-1]

  for n in soup.select('div.contLineaTitulo'):
    
    item = {}
    item['title']     = n.h1.text
    item['link']      = n.a['href']
    item['guid']      = re.compile('\d+').findall(item['link'])[0]
    item['category']  = category
    item['thumbnail'] = n.img['src'] if n.img else None
    item['subheader'] = n.p.text
    builder.add_item(item)

  return builder.get_value()

def rss_noticia(args):

  full_url = 'http://www.pregon.com.ar/nota/%s/dummy.html' % args['host']

  soup = BeautifulSoup(read_clean(full_url, use_cache=False))
  today_date = get_header_date(soup.select('div.clima div')[-1].text)

  builder = XMLBuild(conf, today_date)

  body = soup.select('div.main div.col1')[0]
 
  divimg = body.find_all('div',{'class':'fotonota'})

  item = {}
  item['title']     = body.h1.text
  item['category']  = body.h2.text
  item['link']      = full_url
  item['guid']      = args['host']
  item['thumbnail'] = divimg[0].img['src'] if len(divimg) else None
  item['pubDate']   = date2iso(get_noticia_date(body.strong.text))
  item['content']   = body.find_all('div',{'class':'cc2'})[0].p.__repr__().decode('utf-8')
  
  builder.add_item(item)
  return builder.get_value()

def rss_funebres(args):

  soup = BeautifulSoup(read_clean('http://www.pregon.com.ar/subseccion/2/1/funebres.html', use_cache=False))
  today_date = get_header_date(soup.select('div.clima div')[-1].text)

  # Obtenemos las url funebres
  urls = {}
  for n in soup.select('div.contLineaTitulo h1 a'):
    urls[n['href']] = None

  builder = XMLBuild(conf, today_date)

  def handle_result(rpc, url):
    result = rpc.get_result()
    if result.status_code == 200: 
      soup = BeautifulSoup(clean_content(result.content))
      content = soup.select('div.main div.col1 div.cc2')[0].__repr__().decode('utf-8')
      #content = re.compile(r'<br.*?/>').sub('', content)
      #content = re.sub(r'<([a-z][a-z0-9]*)([^>])*?(/?)>', r'<\1>', content)

      tmp = get_noticia_date(soup.select('div.main div.col1 strong')[0].text)

      item = {}
      item['title']       = 'Sepelios %s' % tmp.strftime('%d/%m')
      item['description'] = content
      item['link']        = url
      item['guid']        = re.compile('\d+').findall(item['link'])[0]
      item['pubDate']     = tmp.strftime("%a, %d %b %Y %H:%M:%S")
      item['category']    = 'Sepelios %s' % tmp.strftime('%d/%m')

      builder.add_funebre(item)

  # Traemos en paralelo (primeras 4)
  multi_fetch(urls.keys()[:4], handle_result)

  # HACK POR EL DIA (no se muestra nunca el LAST FUNEBRE)
  builder.add_funebre({})
  
  return builder.get_value()


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
      'has_clasificados' : False,
      'has_funebres'     : 'funebres://',
      'has_farmacia'     : False,
      'has_cartelera'    : False,
    },
    'config': {
        'android': { 'ad_mob': 'a1521debeb75556', 'google_analytics' : ['UA-32663760-5'] },
        'iphone':  { 'ad_mob': 'a1521debeb75556', 'google_analytics' : ['UA-32663760-5'] },
        'ipad':    { 'ad_mob': 'a1521debeb75556', 'google_analytics' : ['UA-32663760-5'] }
    }
  } 