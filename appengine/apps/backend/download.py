# -*- coding: utf-8 -*-
import logging
import feedparser
import hashlib
#import requests
import urllib2

from email.utils import parsedate
from datetime import datetime

from BeautifulSoup import BeautifulSoup

from google.appengine.api import files, taskqueue

from google.appengine.ext import db, blobstore
from google.appengine.api.images import get_serving_url

from webapp2 import RequestHandler

from utils import do_slugify
from utils import FrontendHandler, get_or_404
from utils import apps_id, in_cache, drop_cache, build_inner_url, get_xml, get_mapping, read_cache, get_httpurl, get_lastmodified
from utils import HtmlBuilderMixing, Jinja2Mixin

from lhammer.xml2dict import XML2Dict


class DownloadAll(RequestHandler, HtmlBuilderMixing, Jinja2Mixin):

  def download_article(self, **kwargs):
    self.request.charset = 'utf-8'
    appid   = self.request.params.get('appid')
    article = self.request.params.get('article')
    
    section = None
    link = None
    es_eldia = appid == 'eldia' or appid=='com.diventi.eldia'
    if es_eldia: 
      link    = self.request.params.get('link')
      section = self.request.params.get('section')
    
    # Iteramos todas las noticias de la seccion y las mandamos a bajar // 1h
    url   = 'noticia://%s' % article
    count = 0
    for size in ['small', 'big']:

      inner_url = build_inner_url('html', appid, url, size)

      # Esta en cache?
      if in_cache(inner_url) and es_eldia:
        cc = read_cache(inner_url)
        assert(cc != None)
        
        if es_eldia: 
          http_url = link
        else:
          http_url, _, _, _, _ = get_httpurl(appid, url, size=size) 
        
        last, code = get_lastmodified(http_url)
        assert(code == 200)
        

        # Estaba en cache, pero fecha distinta ... lo "re-armo"
        if cc[2] != last:
          self.re_build_html_and_images(appid, url, size, 'pt')
          count = count + 1
        continue
      
      # No estaba en cache, lo "armo"
      self.build_html_and_images(appid, url, size, 'pt', use_cache=(size=='big'))

  def download_section(self, **kwargs):
    self.request.charset = 'utf-8'
    appid   = self.request.params.get('appid')
    section = self.request.params.get('section')

    #logging.error('>> DOWNLOADING SECTION %s' % section)
    # Borro las "decoraciones" seccion y las rearmo
    self.re_build_html_and_images(appid, 'menu_section://%s' % section, 'big', 'pt')
    self.re_build_html_and_images(appid, 'ls_menu_section://%s' % section, 'big', 'ls')
    
    #logging.error('>> DOWNLOADING SECTION %s - #2' % section)
    
    # Borramos las seccion y la rearmamos
    self.re_build_html_and_images(appid, 'section://%s' % section, 'big',   'pt')
    self.re_build_html_and_images(appid, 'section://%s' % section, 'small', 'pt')
    
    #logging.error('>> DOWNLOADING SECTION %s - #3' % section)
    
    # Iteramos todas las noticias de la seccion y las mandamos a bajar
    xmlstr, _ = get_xml(appid, 'section://%s' % section, use_cache=True)
    xml = XML2Dict().fromstring(xmlstr.encode('utf-8'))
    if 'item' in xml.rss.channel:
      for i in xml.rss.channel.item:
        #if appid != 'ecosdiarios' or appid!='com.diventi.ecosdiarios': continue
        if appid == 'eldia' or appid=='com.diventi.eldia': 
          taskqueue.add(queue_name='download2', url='/download/article', params={'appid': appid, 'article': i.guid.value, 'link': i.link, 'section':section})
          #logging.error('--------- llame a bajar noticia:' + i.guid.value)
          continue
        taskqueue.add(queue_name='download2', url='/download/article', params={'appid': appid, 'article': i.guid.value})
      
  def download_newspaper(self, **kwargs):
    
    self.request.charset = 'utf-8'
    appid = self.request.params.get('appid')

    # Rebuild MENU ()
    self.re_build_html_and_images(appid, 'menu://', 'small', 'pt')
    self.re_build_html_and_images(appid, 'menu://', 'big',   'pt')

    # Iteramos todas las secciones y las mandamos a bajar
    xmlstr, _ = get_xml(appid, 'menu://', use_cache=True)
    xml = XML2Dict().fromstring(xmlstr.encode('utf-8'))
		
    try:
      sections = [i.guid.value for i in xml.rss.channel.item] + ['main']
    except:
      logging.error('>> FAILED appid %s' % appid)


    for section in sections:
      # logging.error('>> trying section %s  // appid %s' % (section, appid))
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
    xmlstr, _ = get_xml(appid, 'clasificados://list', use_cache=True)
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
