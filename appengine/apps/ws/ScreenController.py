# -*- coding: utf-8 -*-
import logging
import StringIO
import urllib2
import re
import importlib

from datetime import datetime, timedelta
from HTMLParser import HTMLParser

from hashlib import sha1

from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED

from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api import taskqueue
from google.appengine.api import memcache

from webapp2 import cached_property
from webapp2_extras import json
from utils import FrontendHandler, HtmlBuilderMixing, get_or_404, read_clean, date2iso, get_xml
from utils import apps_id, build_inner_url, get_mapping, get_httpurl

extension_dict = {
    'noticia://'             : 'a',
    'section://'             : 's',
    'clasificados://'        : 's',
    'menu://'                : 'm',
    'funebres://'            : 's',
    'farmacia://'            : 's',
    'cartelera://'           : 's',
    'menu_section://'        : 'ms',
    'ls_menu_section://'     : 'ms',
}

def get_filenames(url):
  name = sha1(url[0:(url.index('?') if '?' in url else None)]).digest().encode('hex')
  extension = extension_dict[ url[0:url.index('/')+2] ]

  names = {'content': '%s.%s' % (name, extension), 
           'images' : '%s.mi' % (name) }
  
  return names


class ScreenController(FrontendHandler, HtmlBuilderMixing):  
  # def test(self, **kwargs):
  #   logging.error('url ==> %s' % self.request.params['url'])

  def get_xml(self, **kwargs):  
    
    appid = self.request.params['appid'] # nombre de la app
    url   = self.request.params['url']   # url interna

    r = get_xml(appid, url, use_cache=True)
    
    self.response.headers['Content-Type'] ='text/xml'
    
    return self.response.write(r)
      
  def get_html(self, **kwargs):  
    appid = self.request.params['appid'] # nombre de la app
    url   = self.request.params['url']   # url interna
    size  = self.request.params['size']  # small, big
    ptls  = self.request.params['ptls']  # pt, ls
    
    content, images = self.build_html_and_images(appid, url, size, ptls)
    
    # self.response.write(apps_id[appid])
    # return
    
    # Set up headers for browser to correctly recognize HTML
    self.response.headers['Content-Type'] ='text/html'
    self.response.write(content)
    return
    
  def add_screen(self, outfile, appid, url, size, ptls):

    content, images = self.build_html_and_images(appid, url, size, ptls)    
    file_names = get_filenames(url)

    outfile.writestr(file_names['content'], content.encode('utf-8'))
    if len(images):
      outfile.writestr(file_names['images'], ','.join(images))

  def get_screen(self, **kwargs):  
    # Parametros del request
    appid = self.request.params['appid'] # nombre de la app
    url   = self.request.params['url']   # url interna
    size  = self.request.params['size']  # small, big
    ptls  = self.request.params['ptls']  # pt, ls
    
    # compress files and emit them directly to HTTP response stream
    output = StringIO.StringIO()
    outfile = ZipFile(output, "w", ZIP_DEFLATED)

    self.add_screen(outfile, appid, url, size, ptls)
    
    if url == 'section://main':
      self.add_screen(outfile, appid, 'menu://', size, ptls)
      fnc = get_mapping(appid)
      outfile.writestr('config.json', json.encode(fnc['config']).encode('utf-8'))

    if url.startswith('noticia://') and size == 'big':
      match = re.compile('section=(\w+)').findall(url)
      section = match[0] if len(match) else 'main'
      #logging.error(' TITULO de section:: %s' % section)
      self.add_screen(outfile, appid, 'menu_section://%s' % section, size, 'pt' )
      self.add_screen(outfile, appid, 'ls_menu_section://%s' % section, size, 'ls' )
    
    outfile.close()
    
    # Set up headers for browser to correctly recognize ZIP file
    self.response.headers['Content-Type'] ='application/zip'
    self.response.headers['Content-Disposition'] = 'attachment; filename="screen.zip"'
    self.response.out.write(output.getvalue())
