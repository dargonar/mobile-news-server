# -*- coding: utf-8 -*-
import logging
import re
import threading

from bs4 import BeautifulSoup
from collections import OrderedDict
from datetime import datetime, timedelta
from utils import days, months_min, date_add_str, read_clean, clean_content, multi_fetch, date2iso
from xmlbuild import XMLBuild

conf = {  'title'       : u'DIARIO EL NORTE',
          'url'         : u'http://www.diarioelnorte.com.ar/',
          'description' : u'Diario El Norte - San Nicolás de los Arroyos',
          'copyright'   : u'EL NORTE Editora y Periodística S.A. - Copyright 1996-2013',
          'logo'        : u'http://diarioelnorte.com.ar/images/logo.png' }


def get_guid(href):
  guid = href.split('_')[0] 
  if 'http://' in href:
    matches = re.compile('.ar/(.+)_').findall(href)
    guid = '#'
    if len(matches)>0:
      guid      = matches[0]
  return guid
  
def fullpath(path):
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

# 29 Oct 2013 (07:00) | # 29 Oct 2013 |
def get_noticia_date(strdate):
  parts = strdate.split('|')[0].strip().split(' ')
  
  day=int(parts[0])
  month = parts[1].lower() if parts[1].lower()!='set' else 'sep'
  inx = months_min.index(month)
  year = int(parts[2])
  if len(parts)>3:
    hh, mm = parts[3][1:-1].split(':')  
    return datetime(year=year, month=inx+1, day=day, hour=int(hh), minute=int(mm), second=00)
  
  return datetime(year=year, month=inx+1, day=day)
  
# Martes. 29-10-2013
def get_header_date(strdate):
  parts = strdate.split('. ')[1].strip().split('-')
  return datetime(year=int(parts[2]), month=int(parts[1]), day=int(parts[0]))

# 07:00 | 
def get_main_noticia_date(strdate, today_date):
  hh, mm = strdate.split('|')[0].strip().split(':')
  return today_date+timedelta(hours=int(hh), minutes=int(mm))

def get_index_item(element, today_date, is_main=False, category=None):
  head          = element.h2.a if is_main else element.h3.a
  article_date  = None
  if is_main:
    article_date  = get_main_noticia_date(element.find_all('span',{'class':'time'})[0].text, today_date) #07:00 | 
  else:
    article_date  = get_noticia_list_date(element.find_all('span',{'class':'time'})[0].text, today_date) 
  
  img_div = None
  if is_main:
    img_container = element.find_all('div',{'class':'two-cols'})
    if len(img_container)>0:
      img_container = img_container[0].find_all('div',{'class':'col1'})
      if len(img_container)>0:
        img_div       = img_container[0]
  else:
    img_container = element.find_all('div',{'class':'image'})
    if len(img_container)>0:
      img_div       = img_container[0]
  
  sub_h         = element.find_all('p',{'class':'excerpt'})[0]
  if sub_h and sub_h.span:
    spantime      = sub_h.span.extract()
  
  item = {}
  item['title']     = head.text
  item['link']      = fullpath(head['href'])
  item['guid']      = get_guid(head['href']) #head['href'].split('_')[0]
  item['pubDate']   = article_date.strftime("%a, %d %b %Y %H:%M:%S") 
  item['rawDate']   = article_date
  item['category']  = element.h5.text if category is None else category
  item['thumbnail'] = fullpath(img_div.a.img['src']) if img_div and img_div.a and img_div.a.img else None
  item['subheader'] = sub_h.text if sub_h else None
  
  return item    
  
def get_index_tabbed_item(element, today_date):
  title          = element.find_all('div',{'class':'content'})[0].h3.text
  link           = element.find_all('a',{'class':'more'})[0]
  article_date   = get_main_noticia_date(element.find_all('span',{'class':'time'})[0].text, today_date) 
  
  img_div = None
  img_container = element.find_all('div',{'class':'image'})
  if len(img_container)>0:
    img_div       = img_container[0]

  sub_h         = element.find_all('p',{'class':'excerpt'})
  if len(sub_h)>0:
    sub_h=sub_h[0]
    amore=sub_h.a.extract()
    spantime=sub_h.span.extract()
  else:
    sub_h=None
    
  item = {}
  item['title']     = title
  item['link']      = fullpath(link['href'])
  item['guid']      = get_guid(link['href'])
  item['pubDate']   = article_date.strftime("%a, %d %b %Y %H:%M:%S") 
  item['rawDate']   = article_date
  item['category']  = 'Deportes'
  item['thumbnail'] = fullpath(img_div.a.img['src']) if img_div and img_div.a and img_div.a.img else None
  item['subheader'] = sub_h.text if sub_h else None
  
  return item    

def get_index_mini_heading(element, today_date):
  head           = element.h4.a
  
  sub_h         = element.find_all('p',{'class':'excerpt'})
  if len(sub_h)>0:
    sub_h=sub_h[0].text
  else:
    sub_h=None
    
  item = {}
  item['title']     = head.text
  item['link']      = fullpath(head['href'])
  item['guid']      = get_guid(head['href'])
  #item['pubDate']   = article_date.strftime("%a, %d %b %Y %H:%M:%S") 
  item['rawDate']   = today_date
  item['category']  = element.h5.text.split('|')[0].strip()
  #item['thumbnail'] = fullpath(img_div.a.img['src']) if img_div and img_div.a and img_div.a.img else None
  item['subheader'] = sub_h.__repr__().decode('utf-8') if sub_h else None
  
  return item    

def rss_index(args):
  soup = BeautifulSoup(read_clean('http://www.diarioelnorte.com.ar/', use_cache=False))
#  soup = BeautifulSoup(urlopen('http://www.diarioelnorte.com.ar/', timeout=25).read())
  today_date = get_header_date(soup.select('#hoc #hic div.middle span.date')[0].text)
  builder = XMLBuild(conf, today_date)
  
  notas = soup.select('#content div.left div.main-article ')+soup.select('#content div.left div.two-cols div.col1 div.article')+soup.select('#content div.left div.two-cols div.col2 div.article')
  for i in xrange(len(notas)):
    item = get_index_item(notas[i], today_date, is_main=('main-article' in notas[i]['class']))
    if item is not None: builder.add_item(item)    
  
  notas = soup.select('#content div.left div.widget #sport-tabs div.ui-tabs-panel')
  for i in xrange(len(notas)):
    item = get_index_tabbed_item(notas[i], today_date)
    if item is not None: builder.add_item(item)    
    
  notas1 = soup.select('#content div.left div.mini-headings div.col1 div.article')
  notas2 = soup.select('#content div.left div.mini-headings div.col2 div.article')
  notas3 = soup.select('#content div.left div.mini-headings div.col3 div.article')
  
  for i in xrange(max(len(notas1), len(notas2), len(notas3))):
    if len(notas1)>i:
      item = get_index_mini_heading(notas1[i], today_date)
      if item is not None: builder.add_item(item)    
    if len(notas2)>i:
      item = get_index_mini_heading(notas2[i], today_date)
      if item is not None: builder.add_item(item)    
    if len(notas3)>i:
      item = get_index_mini_heading(notas3[i], today_date)
      if item is not None: builder.add_item(item)    
  
  return builder.get_value()

def rss_menu(args):
  
  soup = BeautifulSoup(read_clean('http://www.diarioelnorte.com.ar/', use_cache=False))
  today_date = get_header_date(soup.select('#hoc #hic div.middle span.date')[0].text)
  
  builder = XMLBuild(conf, today_date)

  for cat in soup.select('#hoc #hic div.bottom div.left ul.mainmenu li a'):
    if cat.text.lower().strip() in ['inicio' , u'necrológicas' , u'clasificados']:
      continue
    link = fullpath(cat['href'])
    guid = cat['href'] 
    item = {}
    item['title']     = cat.text
    item['link']      = cat['href']
    item['guid']      = guid.strip()
    # item['pubDate']   = date_add_str(today_date, '00:00')
    builder.add_section(item)
  
  for cat in soup.select('#hoc #hic div.bottom div.left ul.submenu2 li a'):
    if cat.text.lower().strip() in ['locales' , u'necrológicas' , u'clasificados']:
      continue
    link = fullpath(cat['href'])
    guid = cat['href'] 
    item = {}
    item['title']     = cat.text
    item['link']      = cat['href']
    item['guid']      = guid.strip()
    # item['pubDate']   = date_add_str(today_date, '00:00')
    builder.add_section(item)
  
  return builder.get_value()
  
def rss_seccion(args):
  
  if 'sub_seccion' in args['host'].lower():
    return rss_sub_seccion(args)
  
  full_url = 'http://www.diarioelnorte.com.ar/%s' % args['host'].lower()
  soup = BeautifulSoup(read_clean(full_url, use_cache=False))
  today_date = get_header_date(soup.select('#hoc #hic div.middle span.date')[0].text)
  builder = XMLBuild(conf, today_date)
  
  cats1 = soup.select('#content div.left div.two-cols div.col1 div.category')
  cats2 = soup.select('#content div.left div.two-cols div.col2 div.category')
  
  for i in xrange(max(len(cats1), len(cats2))):
    if len(cats1)>i:
      items = get_category_items(cats1[i], today_date)
      if items and len(items)>0: 
        for item in items:
          builder.add_item(item)    
    if len(cats2)>i:
      items = get_category_items(cats2[i], today_date)
      if items and len(items)>0: 
        for item in items:
          builder.add_item(item)    
    
  return builder.get_value()

def get_category_items(cat, today_date):
  category = cat.h5.text
  items = []
  for cat_item in cat.select('div.article'):
    article_date  = get_noticia_list_date(cat_item.find_all('span',{'class':'time'})[0].text, today_date) 
    
    sub_h         = cat_item.find_all('p',{'class':'excerpt'})[0]
    if sub_h and sub_h.span:
      spantime      = sub_h.span.extract()
    
    img_div=None
    img_container = cat_item.find_all('div',{'class':'image'})
    if len(img_container)>0:
      img_div       = img_container[0]
    
    item = {}
    item['title']     = cat_item.h3.a.text
    item['link']      = fullpath(cat_item.h3.a['href'])
    item['guid']      = get_guid(cat_item.h3.a['href'])
    item['pubDate']   = article_date.strftime("%a, %d %b %Y %H:%M:%S") 
    item['rawDate']   = article_date
    item['category']  = category
    item['thumbnail'] = fullpath(img_div.a.img['src']) if img_div and img_div.a and img_div.a.img else None
    item['subheader'] = sub_h.text if sub_h else None
    items.append(item)
  return items
  
def rss_sub_seccion(args):
  
  full_url = 'http://www.diarioelnorte.com.ar/%s' % args['host'].lower()
  soup = BeautifulSoup(read_clean(full_url, use_cache=False))
  today_date = get_header_date(soup.select('#hocj #hic div.middle span.date')[0].text)
  builder = XMLBuild(conf, today_date)
  
  category = soup.select('#content div.left div.main-article')[0].h5.text
  #category = soup.select('#content div.left div.main-article')[0].find_all('h5',{'class':'sub'})[0].text
  
  notas = soup.select('#content div.left div.main-article div')
  for i in xrange(len(notas)):
    item = get_index_item(notas[i], today_date, is_main=False, category=category)
    if item is not None: builder.add_item(item)    
    
  return builder.get_value()

def rss_noticia(args): 
  
  full_url = 'http://diarioelnorte.com.ar/%s_dummy.html' % args['host']
  # httpurl=u'http://www.diariolareforma.com.ar/2013/activistas-suspenden-la-audiencia-concedida-a-hernan-perez-orsi/'
  # soup = BeautifulSoup(urlopen(httpurl, timeout=25).read())
  soup = BeautifulSoup(read_clean(full_url, use_cache=False))
  
  item, today_date = get_noticia_item(soup, full_url, args)
  builder = XMLBuild(conf, today_date)
  builder.add_item(item)
  return builder.get_value()
  
def get_noticia_item(soup, full_url, args=None):
  
  today_date = get_header_date(soup.select('#hoc #hic div.middle span.date')[0].text)
  
  body = soup.select('#content div.left div.main-article')[0]
  
  article_date  = get_noticia_date(body.find_all('span',{'class':'time'})[0].text) 

  img_div=None
  img_container = body.find_all('div',{'class':'image'})
  if len(img_container)>0:
    img_div       = img_container[0]
  
  content = body.find_all('div',{'class':'excerpt'})[0]
  
  # quito el span de la fecha del content, dado que ya la utilice y no debo mostrarla.
  if content and content.span:
    spantime      = content.span.extract()
  
  # obtengo el subheader extrayendoselo del content.
  sub_h  = content.find_all('p')[0].extract()
  if sub_h and sub_h.strong:
    sub_h = sub_h.strong
  
  #obtengo la iamgen extrayendosela del content.
  images      = content.find_all('div',{'class','image'})
  if len(images)>0:
    image = content.find_all('div',{'class','image'})[0].extract()
  
  # armo el content con los 'p' que quedaron vivos.
  content_string = u''
  if args:
    for p in content.find_all('p'):
      del p['class']
      del p['style']
      content_string = content_string + p.__repr__().decode('utf-8')
  else:
    content_string =content.text
    
  # le sumo al content el autor de la nota si existe.
  footer = body.find_all('div',{'class':'footer'})
  if args and len(footer)>0:
    footer=footer[0]
    del footer['class']
    del footer['style']
    content_string = content_string + '<p>%s</p>' % footer.__repr__().decode('utf-8')
  
  item = {}
  item['title']     = body.h2.text
  item['category']  = body.find_all('span',{'class':'category'})[0].text
  item['link']      = full_url
  item['guid']      = args['host'] if args else get_guid(full_url)
  item['thumbnail'] = fullpath(img_div.a.img['src']) if img_div and img_div.a and img_div.a.img else None
  item['pubDate']   = article_date.strftime("%a, %d %b %Y %H:%M:%S") 
  item['rawDate']   = article_date
  item['content']   = content_string
  item['subheader'] = sub_h.text if sub_h else ''
  
  return item, today_date

def rss_funebres(args):

  full_url = 'http://diarioelnorte.com.ar/necrologicas.html'
  soup = BeautifulSoup(read_clean(full_url, use_cache=False))
  #soup = BeautifulSoup(urlopen(full_url, timeout=25).read())
  today_date = get_header_date(soup.select('#hocj #hic div.middle span.date')[0].text)
  
  body = soup.select('#content div.left div.main-article')[0]
  
  article_date  = get_noticia_date(body.find_all('span',{'class':'time'})[0].text) 
  
  category = body.h2.text
  builder = XMLBuild(conf, today_date)
  
  for p in body.select('div.excerpt p'):
    del p['class']
    del p['style']

    text = p.text #__repr__().decode('utf-8')
    if text =='' or text.lower()=='avisos funebres' or text=='<br>':
      print 'puto'
      continue
    print 'ORKOT'
    item = {}
    item['title']     = ''
    item['link']      = full_url
    item['guid']      = '?'
    #item['pubDate']   = article_date.strftime("%a, %d %b %Y %H:%M:%S") 
    item['rawDate']   = article_date
    item['category']  = category
    item['description'] = text
    
    builder.add_funebre(item)    
      
  builder.add_funebre({})
  
  return builder.get_value()

def rss_clasificados(args):

  builder = XMLBuild(conf, datetime.now())
  
  for _id, title in get_classifieds().items():
    item = {}
    item['title'] = title
    item['link']  = 'clasificados://%s' % _id
    item['guid']  = _id

    builder.add_item(item)

  return builder.get_value()

def get_classifieds():
  
  soup = BeautifulSoup(read_clean('http://diarioelnorte.com.ar/clasificados.php', use_cache=False))
  
  items = OrderedDict([])
  
  cats = soup.select('#content div.col1 div.category')+soup.select('#content div.col2 div.category')+soup.select('#content div.center div.category')
  
  for i in xrange(len(cats)):
    item=cats[i]
    if item.h5.span.text.strip().lower()!='0 avisos':
      items.update({item.h1.span.text.strip():item.h1.span.text.strip()})
  return items

def rss_clasificados_section(args): # falta
  # traemos el listado para ver a q url tenemos que pegarle
  soup = BeautifulSoup(read_clean('http://diarioelnorte.com.ar/clasificados.php', use_cache=True))
  section_name = args['host'].lower()
  today_date = get_header_date(soup.select('#hocj #hic div.middle span.date')[0].text)
  
  cats = soup.select('#content div.col1 div')+soup.select('#content div.col2 div')+soup.select('#content div.center div')
  urls = {}
  section_name = 'automotores'
  for i in xrange(len(cats)):
    item=cats[i]
    if 'category' not in item['class']:
      continue
    #print '-- ' + item.h1.span.text.lower().strip()
    if item.h1.span.text.lower().strip()!=section_name:
      continue
    # estoy parado en la categoria, me tengo que ir al next sibling
    next_item = item.find_next_siblings('div', limit=1)[0]
    while next_item and 'sport-heading' in next_item['class']:
      a=next_item.h3.select('a')
      if len(a)==0:
        next_item = next_item.find_next_siblings('div', limit=1)
        if len(next_item)>0:
          next_item = next_item[0]
        else:
          next_item=None
        continue
      urls[fullpath(next_item.h3.a['href'])] = None
      next_item = next_item.find_next_siblings('div', limit=1)
      if len(next_item)>0:
        next_item = next_item[0]
      else:
        next_item=None
    break
  
  funlock  = threading.Lock()
  items = []
  
  def handle_result(rpc, url):
    result = rpc.get_result()
    if result.status_code == 200: 
      
      soup = BeautifulSoup(clean_content(result.content))
      avisos = get_items_clasificados(soup)
      with funlock:
        for item in avisos:
          items.append(item)

  # Traemos en paralelo (primeras 4)
  multi_fetch(urls.keys()[:8], handle_result)
  
  builder = XMLBuild(conf, today_date)
  for item in sorted(items, key=lambda x: x['category'], reverse=False):
    builder.add_item(item)
  
  return builder.get_value()

def get_items_clasificados(soup):
  category = soup.select('#coc div.category h2 span.gris')[0].text.strip().split('|')[1]
  div = soup.select('#coc #content2 div.col3')[0].find('div')
  items = []
  now=datetime.now().strftime("%a, %d %b %Y %H:%M:%S")  
  while div and div.name =='div':
    item = {}
    item['title']       = div.select('div.category h3 span')[0].text
    item['description'] = div.select('p.excerpt')[0].text
    item['category']    = category
    item['pubDate']     = now
    items.append(item)
    div = div.find_next_siblings('div', limit=1)
    if len(div)>0:
      div = div[0]
    else:
      div=None
  return items
    
def rss_cartelera(args):
  
  soup = BeautifulSoup(read_clean('http://diarioelnorte.com.ar/seccion_cartelera.html', use_cache=False))
  today_date = get_header_date(soup.select('#hoc #hic div.middle span.date')[0].text)
  
  builder = XMLBuild(conf, today_date)

  # Obtenemos las url de cada item de cartelera
  urls = {}
  
  cats1 = soup.select('#content div.left div.two-cols div.col1 div.category')
  cats2 = soup.select('#content div.left div.two-cols div.col2 div.category')
  
  for i in xrange(max(len(cats1), len(cats2))):
    if len(cats1)>i:
      for cat_item in cats1[i].select('div.article'):
        urls[fullpath(cat_item.h3.a['href'])] = None
    if len(cats2)>i:
      for cat_item in cats2[i].select('div.article'):
        urls[fullpath(cat_item.h3.a['href'])] = None
  
  funlock  = threading.Lock()
  items = []
  
  def handle_result(rpc, url):
    result = rpc.get_result()
    if result.status_code == 200: 
      
      soup = BeautifulSoup(clean_content(result.content))
      item, today_date = get_noticia_item(soup, url)
      with funlock:
        items.append(item)

  # Traemos en paralelo (primeras 4)
  multi_fetch(urls.keys()[:8], handle_result)
  
  builder = XMLBuild(conf, today_date)
  for item in sorted(items, key=lambda x: x['rawDate'], reverse=False):
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
      'has_clasificados' : 'clasificados://list',
      'has_funebres'     : 'funebres://',
      'has_farmacia'     : 'http://diarioelnorte.com.ar/farmacias-de-turno.html',
      'has_cartelera'    : 'cartelera://',
    },
    'config': {
        'android': { 'ad_mob': '', 'google_analytics' : ['UA-32663760-3'] },
        'iphone':  { 'ad_mob': '', 'google_analytics' : ['UA-32663760-3'] },
        'ipad':    { 'ad_mob': '', 'google_analytics' : ['UA-32663760-3'] }
    }
  } 