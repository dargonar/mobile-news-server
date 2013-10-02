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

# Necochea, viernes 16 de agosto 2013
def get_header_date(strdate):
  parts = filter(lambda a: a != 'de', strdate.split())[2:]
  inx = months.index(parts[1].lower())
  return datetime(int(parts[2]), inx+1, int(parts[0]))

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
  soup = BeautifulSoup(read_clean('http://www.ecosdiariosweb.com.ar/', use_cache=False))
  today_date = get_header_date(soup.select('div#top_menu p')[-1].text)

  builder = XMLBuild(conf, today_date)

  tmp = soup.select('table.blog table.contentpaneopen')
  for i in xrange(len(tmp)/2): 
    head, body = tmp[2*i], tmp[2*i+1]
    p = body.find_all('p')

    item = {}
    item['title']     = head.tr.a.text.strip()
    item['link']      = '%s/%s' % (main_url, head.tr.a['href'])
    item['guid']      = re.compile('&id=(\d+)').findall(item['link'])[0]
    item['category']  = body.tr.td.span.text.strip()
    item['thumbnail'] = ('%s/%s' % (main_url, p[0].img['src'])) if len(p) > 1 and p[0].img is not None else None
    item['subheader'] = p[-1].text
    builder.add_item(item)

  return builder.get_value()

def rss_menu(args):
  
  soup = BeautifulSoup(read_clean('http://www.ecosdiariosweb.com.ar/', use_cache=False))
  today_date = get_header_date(soup.select('div#top_menu p')[-1].text)

  builder = XMLBuild(conf, today_date)
  for n in soup.select('div#nav ul')[0].find_all('li')[1].ul.find_all('li'):
    item = {}
    item['title']     = n.a.text
    item['link']      = n.a['href']
    item['guid']      = re.compile('&id=(\d+)').findall(item['link'])[0]
    item['pubDate']   = date_add_str(today_date, '00:00')
    
    # No incluimos 'Fúnebres' ni 'Línea Directa'
    if int(item['guid']) != 7 and int(item['guid']) != 34:
        builder.add_section(item)

  return builder.get_value()

def rss_section(args):

  soup = BeautifulSoup(read_clean('%s/index.php?option=com_content&view=category&layout=blog&id=%s&Itemid=3' % (main_url, args['host']), use_cache=False))
  today_date = get_header_date(soup.select('div#top_menu p')[-1].text)
  
  builder = XMLBuild(conf, today_date)

  category = soup.select('div.componentheading')[0].text
  
  tmp = soup.select('table.blog table.contentpaneopen')
  for i in xrange(len(tmp)/2): 
    head, body = tmp[2*i], tmp[2*i+1]
    p = body.find_all('p')
    
    item = {}
    item['title']     = head.tr.a.text.strip()
    item['link']      = '%s/%s' % (main_url, head.tr.a['href'])
    item['guid']      = re.compile('&id=(\d+)').findall(item['link'])[0]
    item['category']  = category
    item['thumbnail'] = ('%s/%s' % (main_url, p[0].img['src'])) if len(p) > 1 and p[0].img is not None else None
    item['pubDate']   = date2iso(get_section_date(body.tr.td.text))
    item['subheader'] = p[-1].text
    builder.add_item(item)

  return builder.get_value()

def rss_noticia(args):

  full_url = 'http://www.ecosdiariosweb.com.ar/index.php?option=com_content&view=article&id=%s' % args['host']

  soup = BeautifulSoup(read_clean(full_url, use_cache=False))
  today_date = get_header_date(soup.select('div#top_menu p')[-1].text)

  builder = XMLBuild(conf, today_date)

  tmp = soup.select('table#majtable table.contentpaneopen')
  header, body = tmp[0], tmp[1]

  content = u''
  for p in body.find_all('tr')[1].td.find_all('p'): 
    content = content + p.__repr__().decode('utf-8')
  content = re.compile(r'<img.*?/>').sub('', content)

  p = body.find_all('tr')[1].td.p

  item = {}
  item['title']     = header.tr.td.text
  item['link']      = full_url
  item['guid']      = args['host']
  item['thumbnail'] = ('%s/%s' % (main_url, p.img['src'])) if p and p.img else None
  item['pubDate']   = date2iso(get_section_date(body.tr.td.text))
  item['content']   = content
  
  builder.add_item(item)
  return builder.get_value()

def rss_funebres(args):

  full_url = 'http://www.ecosdiariosweb.com.ar/index.php?option=com_content&view=category&layout=blog&id=7&Itemid=5'

  soup = BeautifulSoup(read_clean(full_url, use_cache=False))
  today_date = get_header_date(soup.select('div#top_menu p')[-1].text)

  builder = XMLBuild(conf, today_date)

  tmp = soup.select('table.blog table.contentpaneopen')
  for i in xrange(len(tmp)/2): 
    head, body = tmp[2*i], tmp[2*i+1]
    date = get_funebre_date(head.tr.td.text)

    content = u''
    if body.find_all('tr')[0].td.p is not None:
      contents = body.find_all('tr')[0].td.find_all('p')
    else:
      contents = body.find_all('tr')[0].td.find_all('div',attrs={'id':'cke_pastebin'})

    for p in contents:
      content = content + p.__repr__().decode('utf-8')

    item = {}
    item['title']       = 'Funebres %s' % date.strftime('%d/%m')
    item['description'] = content
    item['link']        = full_url
    item['guid']        = re.compile('&id=(\d+)').findall(item['link'])[0]
    item['pubDate']     = date2iso(date)
    item['category']    = 'Funebres %s' % date.strftime('%d/%m')

    builder.add_funebre(item)

  # HACK POR EL DIA (no se muestra nunca el LAST FUNEBRE)
  builder.add_funebre({})
  
  return builder.get_value()

def rss_farmacia(args):

  full_url = 'http://www.ecosdiariosweb.com.ar/index.php?option=com_content&view=category&layout=blog&id=9&Itemid=13'

  soup = BeautifulSoup(read_clean(full_url, use_cache=False))
  today_date = get_header_date(soup.select('div#top_menu p')[-1].text)

  builder = XMLBuild(conf, today_date)
  
  tmp = soup.select('div#cke_pastebin')[0].text
  tmp = tmp.replace(u'\n\r',u'</br>')
  tmp = tmp.replace(u'\n',u'</br>')
  
  builder.add_raw(tmp)
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
      'has_clasificados' : 'http://www.ecosdiariosweb.com.ar/clasificados/clasificados.pdf',
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
