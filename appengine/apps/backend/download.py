# -*- coding: utf-8 -*-
import logging
import feedparser
import hashlib

from email.utils import parsedate
from datetime import datetime

from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup

from google.appengine.api import files, taskqueue

from google.appengine.ext import db, blobstore
from google.appengine.api.images import get_serving_url

from webapp2 import RequestHandler

from utils import do_slugify
from utils import FrontendHandler, get_or_404
from utils import apps_id, in_cache, drop_cache, build_inner_url, get_xml, get_mapping
from utils import HtmlBuilderMixing, Jinja2Mixin

from lhammer.xml2dict import XML2Dict


class DownloadAll(RequestHandler, HtmlBuilderMixing, Jinja2Mixin):

  def download_article(self, **kwargs):
    self.request.charset = 'utf-8'
    appid   = self.request.params.get('appid')
    article = self.request.params.get('article')

    # Iteramos todas las noticias de la seccion y las mandamos a bajar // 1h
    url = 'noticia://%s' % article
    for size in ['small', 'big']:
      if in_cache(build_inner_url(appid, url, size)):
        continue
      self.build_html_and_images(appid, url, size, 'pt', use_cache=False)

  def download_section(self, **kwargs):
    self.request.charset = 'utf-8'
    appid   = self.request.params.get('appid')
    section = self.request.params.get('section')

    # logging.error('>> DOWNLOADING SECTION %s' % section)
    # Borro las "decoraciones" seccion y las rearmo
    self.re_build_html_and_images(appid,    'menu_section://%s' % section, 'big', 'pt')
    self.re_build_html_and_images(appid, 'ls_menu_section://%s' % section, 'big', 'ls')

    # Borramos las seccion y la rearmamos
    self.re_build_html_and_images(appid, 'section://%s' % section, 'big',   'pt')
    self.re_build_html_and_images(appid, 'section://%s' % section, 'small', 'pt')

    # Iteramos todas las noticias de la seccion y las mandamos a bajar
    xmlstr = get_xml(appid, 'section://%s' % section, use_cache=True)
    xml = XML2Dict().fromstring(xmlstr.encode('utf-8'))
    if 'item' in xml.rss.channel:
      for i in xml.rss.channel.item:
        if appid != 'ecosdiarios': continue
        taskqueue.add(queue_name='download2', url='/download/article', params={'appid': appid, 'article': i.guid.value})

  def download_newspaper(self, **kwargs):
    
    self.request.charset = 'utf-8'
    appid = self.request.params.get('appid')

    # Rebuild MENU ()
    self.re_build_html_and_images(appid, 'menu://', 'small', 'pt')
    self.re_build_html_and_images(appid, 'menu://', 'big',   'pt')

    # Iteramos todas las secciones y las mandamos a bajar
    xmlstr = get_xml(appid, 'menu://', use_cache=True)
    xml = XML2Dict().fromstring(xmlstr.encode('utf-8'))
		
    try:
      sections = [i.guid.value for i in xml.rss.channel.item] + ['main']
    except:
      logging.error('>> FAILED appid %s' % appid)


    for section in sections:
      logging.error('>> trying section %s  // appid %s' % (section, appid))
      taskqueue.add(queue_name='download2', url='/download/section', params={'appid': appid, 'section': section})
      
  def download_all(self, **kwargs):    
    # Mantenemos una lista de lo que fuimos mandando a bajar
    # por que hay dos appid para ElDia (x ej)
    inverted = dict((v,k) for k,v in apps_id.iteritems())
    for name, appid in inverted.items():
      taskqueue.add(queue_name='download2', url='/download/newspaper', params={'appid':appid})

  def download_one(self, **kwargs):    
    taskqueue.add(queue_name='download2', url='/download/newspaper', params={'appid':kwargs['newspaper']})

  def download_clasificados(self, **kwargs):
    self.request.charset = 'utf-8'
    appid = self.request.params.get('appid')

    self.re_build_html_and_images(appid, 'clasificados://list', 'small', 'pt')
    
    #self.re_build_html_and_images(appid, 'clasificados://list', 'big',   'pt')

    # Iteramos todas los items
    xmlstr = get_xml(appid, 'clasificados://list', use_cache=True)
    xml = XML2Dict().fromstring(xmlstr.encode('utf-8'))

    items = [i.guid.value for i in xml.rss.channel.item]
    for item in items:
      url = 'clasificados://%s' % item
      taskqueue.add(queue_name='download2', url='/download/page', params={'appid': appid, 'url': url})

  def download_page(self, **kwargs):
    self.request.charset = 'utf-8'
    appid = self.request.params.get('appid')
    url   = self.request.params.get('url')

    self.re_build_html_and_images(appid, url, 'small', 'pt')
    self.re_build_html_and_images(appid, url, 'big',   'pt')

  def download_extras(self, **kwargs):    
    inverted = dict((v,k) for k,v in apps_id.iteritems())
    
    for name, appid in inverted.items():
      extras =  get_mapping(appid)['extras']
      
      if extras['has_clasificados'] == 'clasificados://list':
        taskqueue.add(queue_name='download2', url='/download/clasificados', params={'appid':appid})

      if extras['has_funebres']  == 'funebres://':
        taskqueue.add(queue_name='download2', url='/download/page', params={'appid':appid, 'url':extras['has_funebres']})

      if extras['has_farmacia']  == 'farmacia://':
        taskqueue.add(queue_name='download2', url='/download/page', params={'appid':appid, 'url':extras['has_farmacia']})

      if extras['has_cartelera']  == 'cartelera://':
        taskqueue.add(queue_name='download2', url='/download/page', params={'appid':appid, 'url':extras['has_cartelera']})