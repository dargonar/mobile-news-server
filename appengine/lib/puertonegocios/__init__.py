# -*- coding: utf-8 -*-
#from __future__ import unicode_literals

import logging
import re
import threading

from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
from collections import OrderedDict
from datetime import datetime, timedelta
from utils import days, months_min, date_add_str, read_clean, clean_content, multi_fetch, date2iso
from xmlbuild import XMLBuild


# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

conf = {  'title'       : u'PUERTO NEGOCIOS',
          'url'         : u'http://www.puertonegocios.com/',
          'description' : u'Puerto Negocios - Arcadia Consultora - Santa Fe',
          'copyright'   : u'Consultora Arcadia S.A. - Copyright 1996-2014',
          'logo'        : u'http://puertonegocios.com/images/gt06/logo.png' }


def get_guid(href):
  guid = href.split('_')[0] 
  if 'http://' in href:
    matches = re.compile('/index.php/facebook/item/(.+)_').findall(href)
    guid = '#'
    if len(matches)>0:
      guid      = matches[0]
  return guid
  
def fullpath(path):
  if path.startswith('puertonegocios.com/'):
    return 'http://'+path
  if 'http://' in path:
    return path 
  if path[0]=='/':
    return conf['url'][:-1]+path
  return conf['url']+path
  
# 28 Oct (07:00) |   
def get_noticia_list_date(strdate, today_date):
  parts = strdate.split('|')[0].strip().split(' ')
  
  day=parts[0]
  month = parts[1].lower() if parts[1].lower()!='set' else 'sep'
  inx = months_min.index(month)
  
  hh, mm = parts[2][1:-1].split(':')  
  year = today_date.year
  if inx+1 > today_date.month:
    year = today_date.year-1
  return datetime(year=year, month=inx+1, day=int(day), hour=int(hh), minute=int(mm), second=00)

# 08 Jul, 2014
def get_noticia_date(strdate):
  parts = strdate.strip().replace(',','').split(' ')
  
  day=int(parts[0])
  month = parts[1].lower() if parts[1].lower()!='set' else 'sep'
  inx = months_min.index(month)
  year = int(parts[2])
  if len(parts)>3:
    hh, mm = parts[3][1:-1].split(':')  
    return datetime(year=year, month=inx+1, day=day, hour=int(hh), minute=int(mm), second=00)
  
  return datetime(year=year, month=inx+1, day=day)
  
# Martes. 29-10-2013
def get_header_date(soup_obj):
  return datetime.now()

def rss_index(args):
  soup = BeautifulSoup(read_clean(conf['url'], use_cache=False, clean=False))
  #today_date = get_header_date(soup)
  builder = XMLBuild(conf, datetime.now())
  
  notas = soup.select('#gaass200 div.ga-main-item')
  for i in xrange(len(notas)):
    nota = notas[i]
    item = {}
    item['thumbnail'] = fullpath(nota.img['src']) if nota.img else None
    #fullpath(nota.img['src']) if nota.img else None
    item['title']     = UnicodeDammit(nota.div.h4.a.text).unicode_markup
    item['category']  = u'Noticias'
    item['subheader'] = UnicodeDammit(nota.div.p.text).unicode_markup
    item['link']      = fullpath(nota.div.h4.a['href'])
    item['guid']      = fullpath(nota.div.h4.a['href']) #get_guid(nota.div.h4.a['href'])
    #items.append(item)
    builder.add_item(item)    

  notas = soup.select('#innertop div.hnews')
  for i in xrange(len(notas)):
    nota = notas[i]
    item = {}
    item['thumbnail'] = fullpath(nota.img['src']) if nota.img else None
    #fullpath(nota.img['src']) if nota.img else None
    item['title']     = UnicodeDammit(nota.h3.a.text).unicode_markup
    item['category']  = 'Noticias'
    item['subheader'] = UnicodeDammit(nota.p.text).unicode_markup
    item['link']      = fullpath(nota.h3.a['href'])
    item['guid']      = fullpath(nota.h3.a['href']) #get_guid(nota.h3.a['href'])
    #items.append(item)
    builder.add_item(item)    

  notas = soup.select('#innertop div.news-related ul li')
  for i in xrange(len(notas)):
    nota = notas[i]
    if not nota.p:
      continue
    item = {}
    item['thumbnail'] = fullpath(nota.a.img['src']) if nota.a.img else None
    #fullpath(nota.img['src']) if nota.img else None
    item['title']     = UnicodeDammit(nota.p.a.text).unicode_markup
    item['category']  = 'Noticias'
    item['subheader'] = ''
    item['link']      = fullpath(nota.a['href'])
    item['guid']      = fullpath(nota.a['href']) #get_guid(nota.a['href'])
    #items.append(item)
    builder.add_item(item)    

  notas = soup.select('ul#pa-popular li')
  for i in xrange(len(notas)):
    nota = notas[i]
    item = {}
    item['thumbnail'] = None #fullpath(nota.a.img['src']) if nota.img else None
    #fullpath(nota.img['src']) if nota.img else None
    item['title']     = UnicodeDammit(nota.h4.a.text).unicode_markup
    item['category']  = u'Opinión'
    item['subheader'] = ''
    item['link']      = fullpath(nota.h4.a['href'])
    item['guid']      = fullpath(nota.h4.a['href']) #get_guid(nota.h4.a['href'])
    #items.append(item)
    builder.add_item(item)    

  notas = soup.select('div.recent-news ul li')
  for i in xrange(len(notas)):
    nota = notas[i]
    if not nota.p or not nota.p.a:
      continue
    item = {}
    item['thumbnail'] = fullpath(nota.a.img['src']) if nota.a.img else None
    #fullpath(nota.img['src']) if nota.img else None
    item['title']     = UnicodeDammit(nota.p.a.text).unicode_markup
    item['category']  = u'Zoom'
    item['subheader'] = ''
    item['link']      = fullpath(nota.a['href'])
    item['guid']      = fullpath(nota.a['href']) #get_guid(nota.a['href'])
    #items.append(item)
    builder.add_item(item)    


  return builder.get_value()

def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

import cgi    
def rss_menu(args):
  
  soup = BeautifulSoup(read_clean(conf['url'], use_cache=False, clean=False))
  today_date = get_header_date(soup)

  builder = XMLBuild(conf, today_date)

  for cat in soup.select('#header ul.jt-menu li a'):
    if cat.text.lower().strip() in ['puerto negocios', 'contacto', 'facebook']: #'revistas'
      continue
    link = fullpath(cat['href'])
    guid = cat['href'] 
    item = {}
    item['title']     = striphtml(cat.encode(formatter='html').decode('utf8')) if cat.text.lower().strip()!= 'revistas' else 'Ediciones anteriores'
    item['link']      = cat['href']
    item['guid']      = cat['href'] #guid.strip()
    # item['pubDate']   = date_add_str(today_date, '00:00')
    builder.add_section(item)
    
  return builder.get_value()
  
def rss_seccion(args):
  
  full_url = fullpath(args['host'].lower())
  logging.error('------------'+full_url)
  soup = BeautifulSoup(read_clean(full_url, use_cache=False, clean=False))
  today_date = get_header_date(soup)
  builder = XMLBuild(conf, today_date)
  
  if soup.select('#header ul.jt-menu li.active a')[0].text.strip().lower()=='revistas':
    builder = get_revistas(builder, soup)
    soup = BeautifulSoup(read_clean(full_url+'?start=6', use_cache=False, clean=False))
    builder = get_revistas(builder, soup)
    return builder.get_value()
  
  builder = get_noticias_seccion(builder, soup)
  soup = BeautifulSoup(read_clean(full_url+'?start=6', use_cache=False, clean=False))
  builder = get_noticias_seccion(builder, soup)
  return builder.get_value()

def get_revistas(builder, soup):
  notas = soup.select('#itemListLeading div.itemContainer')
  for i in xrange(len(notas)):
    nota = notas[i]
    descarga_link = nota.find_all('div',{'class':'itemAttachmentsBlock'})
    if not descarga_link  or not len(descarga_link) or descarga_link[0].a is None:
      continue
    
    item = {}
    item['thumbnail'] = fullpath(nota.find_all('div',{'class':'catItemImageBlock'})[0].img['src']) if nota.find_all('div',{'class':'catItemImageBlock'})[0].img else None
    item['title']     = nota.find_all('div',{'class':'catItemHeaderText'})[0].span.text 
    item['category']  = 'Ediciones anteriores'
    item['subheader'] = None
    revista_link = fullpath(descarga_link[0].a['href'])
    revista_link = revista_link + '?is_final=1&_item=revista.pdf' if revista_link[-4:] != '.pdf' else revista_link
    item['link']      = revista_link
    item['guid']      = revista_link
    builder.add_item(item)
  return builder
   
def get_noticias_seccion(builder, soup):
  category = soup.select('#header ul.jt-menu li.active a')[0].text
  notas = soup.select('#itemListLeading div.catItemView')
  for i in xrange(len(notas)):
    nota = notas[i]
    item = {}
    item['thumbnail'] = fullpath(nota.img['src']) if nota.img else None
    item['title']     = nota.h3.a.text 
    item['category']  = category
    bajada = nota.find_all('div',{'class':'catItemIntroText'})
    item['subheader'] = re.sub(r'<([a-z][a-z0-9]*)([^>])*?(/?)>', r'<\1>', bajada[0].__repr__().decode('utf-8')) if bajada and len(bajada) else ''
    item['link']      = fullpath(nota.h3.a['href'])
    item['guid']      = fullpath(nota.h3.a['href']) #get_guid(nota.h3.a['href'])
    #items.append(item)
    builder.add_item(item)    

  notas = soup.select('#itemListPrimary div.catItemView')
  for i in xrange(len(notas)):
    nota = notas[i]
    item = {}
    item['thumbnail'] = fullpath(nota.img['src']) if nota.img else None
    item['title']     = nota.h3.a.text 
    item['category']  = category
    bajada = nota.find_all('div',{'class':'catItemIntroText'})
    item['subheader'] = re.sub(r'<([a-z][a-z0-9]*)([^>])*?(/?)>', r'<\1>', bajada[0].__repr__().decode('utf-8')) if bajada and len(bajada) else ''
    item['link']      = fullpath(nota.h3.a['href'])
    item['guid']      = fullpath(nota.h3.a['href']) #get_guid(nota.h3.a['href'])
    #items.append(item)
    builder.add_item(item)    
  return builder


def rss_noticia(args): 
  
  full_url = fullpath(args['host'])
  # httpurl=u'http://www.diariolareforma.com.ar/2013/activistas-suspenden-la-audiencia-concedida-a-hernan-perez-orsi/'
  # soup = BeautifulSoup(urlopen(httpurl, timeout=25).read())
  soup = BeautifulSoup(read_clean(full_url, use_cache=False, clean=False))
  today_date = datetime.now()
  builder = XMLBuild(conf, today_date)
  
  nota = soup.select('#k2Container')[0]
  
  article_date  = get_noticia_date(nota.find_all('span',{'class':'userItemDateCreated'})[0].text) 
  
  cat = soup.select('#header ul.jt-menu li.active a')[0].text.strip() 
  if cat in ['puerto negocios', 'revistas', 'contacto', 'facebook']:
    cat = 'Noticias'
  
  item = {}
  item['title']     = nota.h2.text
  item['category']  = cat
  item['link']      = full_url
  item['guid']      = args['host'] if args else get_guid(full_url)
  img_div = nota.find_all('div',{'class':'imagenNoticia'})
  if img_div and len(img_div)>0:
    item['thumbnail'] = fullpath(img_div[0].img['src']) if img_div[0].img else None
  item['pubDate']   = article_date.strftime("%a, %d %b %Y %H:%M:%S") 
  item['rawDate']   = article_date
  content = nota.find_all('div',{'class':'itemFullText'})
  item['content']   = re.sub(r'<([a-z][a-z0-9]*)([^>])*?(/?)>', r'<\1>', content[0].__repr__().decode('utf-8')) if content and len(content) else ''
  subheader = nota.find_all('div',{'class':'itemIntroText'})
  item['subheader'] = re.sub(r'<([a-z][a-z0-9]*)([^>])*?(/?)>', r'<\1>', subheader[0].__repr__().decode('utf-8')) if subheader and len(subheader) else ''
  
  builder.add_item(item)
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
      
      ('clasificados://list' , {
        'url'    : 'X: rss_clasificados',
        'small'  : {'pt': '9_menu_clasificados.xsl', 'ls': '9_menu_clasificados.xsl'},
        'big'    : None
      }),
     
     ('clasificados://' , {
        'url'    : 'X: rss_clasificados_section',
        'small'  : {'pt': '5_1_clasificados.xsl', 'ls': '5_1_clasificados.xsl'},
        'big'    : {'pt': '5_1_tablet_clasificados.xsl', 'ls': '5_1_tablet_clasificados.xsl'}
      }),
      
      ('cartelera://' , {
        'url'    : 'X: rss_cartelera',
        'small'  : {'pt': '8_1_cartelera.xsl',        'ls': '8_1_cartelera.xsl'},
        'big'    : {'pt': '8_1_tablet_cartelera.xsl', 'ls': '8_1_tablet_cartelera.xsl'}
      }),
    ]),
    'extras': {
      'has_clasificados' : False,
      'has_funebres'     : False,
      'has_farmacia'     : False,
      'has_cartelera'    : False
    },
    'config': {
        'android': { 'ad_mob': '', 'google_analytics' : ['UA-32663760-8'] },
        'iphone':  { 'ad_mob': '', 'google_analytics' : ['UA-32663760-8'] },
        'ipad':    { 'ad_mob': '', 'google_analytics' : ['UA-32663760-8'] }
    }
  } 