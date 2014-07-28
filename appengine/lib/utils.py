# -*- coding: utf-8 -*-
import logging
import urllib
import urllib2
import urlparse
import importlib
import re
#import requests

from HTMLParser import HTMLParser
from dateutil.parser import parser

from re import *
from hashlib import sha1

from lxml import etree
from StringIO import StringIO

from models import CachedContent
from datetime import datetime, timedelta

from lhammer.oodict import OODict
from lhammer.xml2dict import XML2Dict

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import urlfetch

from webapp2 import abort, cached_property, RequestHandler, Response, HTTPException, uri_for as url_for, get_app
from webapp2_extras import jinja2, sessions, json

days       = ['lunes','martes', u'miércoles', 'jueves', 'viernes', u'sábado', 'domingo']
months     = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
months_min = ['ene', 'feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']

apps_id = { 
  'com.diventi.eldia'          : 'eldia',
  'com.diventi.pregon'         : 'pregon',
  'com.diventi.castellanos'    : 'castellanos',
  'com.diventi.ecosdiarios'    : 'ecosdiarios',
  'com.diventi.lareforma'      : 'lareforma',
  'com.diventi.elnorte'        : 'elnorte',
  'com.diventi.puertonegocios' : 'puertonegocios',
}

def multi_fetch(urls, handle_result):
  
  def create_callback(rpc, url):
    return lambda: handle_result(rpc, url)

  rpcs = []
  for url in urls:
    rpc = urlfetch.create_rpc()
    rpc.callback = create_callback(rpc, url)
    urlfetch.make_fetch_call(rpc, url)
    rpcs.append(rpc)

  # Finish all RPCs, and let callbacks process the results.
  for rpc in rpcs:
    rpc.wait()

def date2iso(date):
  return date.strftime("%a, %d %b %Y %H:%M:%S")
 
def date_add_str(today_date, hhmm):
  parts = hhmm.split(':')
  if len(parts)<2: parts = [0,0]
  tmp = today_date + timedelta(minutes=int(parts[1]), hours=int(parts[0]))
  return tmp.strftime("%a, %d %b %Y %H:%M:%S")

def build_inner_url(ctype, appid, url, size=None):
  inx = '?' in url and url.index('?')
  if inx: url = url[0:inx]
  return '%s:%s|%s;%s' % (ctype, appid, url, (size or '') )

def clean_content(content):
  parser = etree.HTMLParser()
  tree   = etree.parse(StringIO(content), parser)
  content = etree.tostring(tree.getroot(), pretty_print=True, method="html")
  return content

def read_url_clean(httpurl, clean=True, encoding=None):

  url           = httpurl
  result        = urllib2.urlopen(url, timeout=25)
  
  content       = result.read()
  h             = result.info()
  last_modified = h['Last-Modified'] if 'Last-Modified' in h.keys() or 'last-modified' in h.keys() else 'now'
  
  # r = requests.get(httpurl, timeout=25)
  # assert(r.status_code == 200)

  # content       = r.text
  # last_modified = r.headers.get('Last-Modified')

  if encoding:
    content=content.decode(encoding).encode('utf-8')
    content=content.replace(encoding,'utf-8')

  if clean:
    content = clean_content(content)

  return content, last_modified

def drop_cache(inner_url):
  memcache.delete(inner_url)
  memcache.delete(inner_url[:inner_url.rindex(';')])
  cc = CachedContent.get_by_key_name(inner_url)
  if cc: cc.delete()

def set_cache(inner_url, content, mem_only=False):
  
  # logging.info('** CACHE SET ** for %s' % inner_url)
  # logging.info('** typeofcontent %s ' % str(type(content[0])) )

  if type(content[0]) != type(unicode()) and type(content[0]) != type(db.Text()):
    content = (content[0].decode('utf-8'), content[1], content[2])

  memcache.set(inner_url, content)

  if not mem_only:      
    cc = CachedContent(key           = db.Key.from_path('CachedContent', inner_url),
                       content       = db.Text(content[0]),
                       images        = db.Text(content[1]),
                       inner_url     = inner_url,
                       last_modified = content[2])
    cc.put()

def in_cache(inner_url):
  # return False #HACK
  dbkey = db.Key.from_path('CachedContent', inner_url)
  return CachedContent.all(keys_only=True).filter('__key__', dbkey).get() is not None

def read_cache(inner_url, mem_only=False):
  # return None #HACK
  content = memcache.get(inner_url)
  if content is None and not mem_only:
    tmp = CachedContent.get(db.Key.from_path('CachedContent', inner_url))
    if tmp is None:
      logging.info('*** NOT IN cache for %s' % inner_url)
      return None
    content = (tmp.content, tmp.images, tmp.last_modified)
    #Lo levanto a memoria, no estaba pero si estaba en disco
    set_cache(inner_url, content, mem_only=True) 
  # logging.info('using cache for %s' % inner_url)
  return content
  
def read_clean(httpurl, clean=True, use_cache=True, encoding=None):
  content = None
  last_modified = None
  # use_cache=False #HACK
  if use_cache:
    cache = memcache.get(httpurl)  
    if cache is not None:
      content, last_modified = cache

  if content is None:
    content, last_modified = read_url_clean(httpurl, clean=clean, encoding=encoding)
    memcache.set(httpurl, (content, last_modified) )
  
  return content, last_modified

_slugify_strip_re = compile(r'[^\w\s-]')
_slugify_hyphenate_re = compile(r'[-\s]+')
def do_slugify(value):
  """
  Normalizes string, converts to lowercase, removes non-alpha characters,
  and converts spaces to hyphens.
  
  From Django's "django/template/defaultfilters.py".
  """
  import unicodedata
  
  if not isinstance(value, unicode):
      value = unicode(value)
  value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
  value = unicode(_slugify_strip_re.sub('', value).strip().lower())
  return _slugify_hyphenate_re.sub('-', value)

def empty(value):
  return value is None or value == ''

def related_link(item):
  return 'noticia://%s?url=%s&title=%sheader=' % (item.attrs.guid, url_fix(item.attrs.url), url_fix(item.value))

def meta_has(meta, media_type):
  if meta is None or meta.attrs is None or not hasattr(meta.attrs, 'has_' + media_type):
    return False

  if getattr(meta.attrs, 'has_' + media_type).lower() != 'true':
    return False  
  
  return True

def gallery(node):
  if node is None or node.group is None:
    return ''
  urls = []
  for c in node.group.content:
    urls.append(c.attrs.url.strip())
  return ';'.join(urls)

def has_content(node, content_type='any_media'):
  if node is None or node.content is None:
    return False
  if content_type == 'any_media':
    content_to_check = ['audio', 'audio/mpeg', 'video']
  else:
    content_to_check = [content_type]
  ret = False

  if type(node.content) != type([]):
    contents = [node.content]
  else:
    contents = node.content

  for content in contents:
    if content.attrs.type in content_to_check:
      ret = True
      break
  return ret

def get_content(node, content_type):

  if node is None or node.content is None:
    return ''

  if type(node.content) != type([]):
    contents = [node.content]
  else:
    contents = node.content

  res = ''
  for content in contents:
    if content.attrs.type == content_type:
      if content_type == 'html':
        res = content.value
      else:
        res = content.attrs.url
      break
  return res

def build_list(value):
  if type(value) == type([]):
    return value

  return [value]

def format_datetime(value, part='%H:%M'):
    if value is None:
      return ''
    p = parser()
    return p.parse(value, default=None, ignoretz=True).strftime(part) #str(value) #

def if_not_none(value):
  if not value:
    return ''

  return value

def noticia_link(node, section_url=None):
  if 'is_final=1' in node.link:
    return node.link
  section = ''
  if section_url is not None and section_url.startswith('section://'):
    section_id = url_fix(section_url.split('://')[1])
    section = u'&section=%s' % (section_id if len(section_id)>0 else 'main')
  else:
    if section_url is not None and section_url.startswith('menu_section://'):
      section_id = url_fix(section_url.split('://')[1])
      section = u'&section=%s' % (section_id if len(section_id)>0 else 'main')
  return 'noticia://%s?url=%s&title=%s&header=%s%s' % (node.guid.value, url_fix(node.link), url_fix(node.title), url_fix(node.description).strip(), section)

def url_fix(s, charset='utf-8'):
    """Sometimes you get an URL by a user that just isn't a real
    URL because it contains unsafe characters like ' ' and so on.  This
    function can fix some of the problems in a similar way browsers
    handle data entered by the user:

    >>> url_fix(u'http://de.wikipedia.org/wiki/Elf (Begriffsklärung)')
    'http://de.wikipedia.org/wiki/Elf%20%28Begriffskl%C3%A4rung%29'

    :param charset: The target charset for the URL if the url was
                    given as unicode string.
    """

    if s is None:
      return ''

    h = HTMLParser()
    s = h.unescape(s)
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))
  
def get_or_404(key):
  try:
      obj = db.get(key)
      if obj:
          return obj
  except db.BadKeyError, e:
      # Falling through to raise the NotFound.
      pass

  abort(404)

class FlashBuildMixin(object):
  def set_error(self, msg):
    self.session.add_flash(self.build_error(msg))
    
  def set_ok(self, msg):
    self.session.add_flash(self.build_ok(msg))
    
  def set_info(self, msg):
    self.session.add_flash(self.build_info(msg))
    
  def set_warning(self, msg):
    self.session.add_flash(self.build_warning(msg))
  
  def build_error(self, msg):
    return { 'type':'error', 'message':msg }
    
  def build_ok(self, msg):
    return { 'type':'success', 'message':msg }
  
  def build_info(self, msg):
    return { 'type':'info', 'message':msg }
    
  def build_warning(self, msg):
    return { 'type':'warning', 'message':msg }

def get_mapping(appid):
  fnc = getattr(importlib.import_module(apps_id[appid]),'get_mapping')
  return fnc()

def get_httpurl(appid, url, size='small', ptls='pt'):  

  # logging.error('-----------------------get_httpurl')
  # logging.error('url[%s]', url)
  
  mapping = get_mapping(appid)

  # Obtenemos el template
  page_name = url.split('?')[0]  
  template  = ''
  httpurl   = ''

  args = {}
  for k in mapping['map']:
    if url.startswith(k):
      httpurl = mapping['map'][k]['url']
      args['host'] = url[url.index('//')+2: (url.index('?') if '?' in url else None) ]
      
      if '?' in url:
        for i in url[url.index('?')+1:].split('&'):
          tmp = i.split('=')
          args[tmp[0]]=tmp[1]
      
      if mapping['map'][k][size]:
        template = mapping['map'][k][size][ptls]
      else:
        template = None
      break
      
  #logging.error(' --------------------------------------- ')
  #logging.error(' - httpurl => [%s] || template => [%s] || url => [%s]' % (httpurl, template, url))
  if httpurl == '' or template == '':
    # logging.error('Something is wrong => [%s]' % (url))
    raise('8-(')

  extras = mapping['extras']
  if extras['has_clasificados']:
    fnc = getattr(importlib.import_module(apps_id[appid]),'get_classifieds')
    extras['clasificados'] = fnc()

  return httpurl, args, template, page_name, extras

def get_xml(appid, url, use_cache=False):
  
  inner_url = build_inner_url('xml', appid, url)
  # use_cache=False #HACK
  result = None
  if use_cache: 
    result = read_cache(inner_url, mem_only=True)
    
  if not result:

    httpurl, args, _, _, _ = get_httpurl(appid, url)
    last_modified = None
    if httpurl.startswith('X:'): 
      # Todos los diarios que crawleamos.
      fnc = getattr(importlib.import_module(apps_id[appid]), httpurl.split()[1])
      result, last_modified = fnc(args)
    else:
      # Todos los diarios que implementan el protocolo (ElDia).
      if '%s' in httpurl: httpurl = httpurl % args['host']
      # El last modified de el read_clean del diaior ElDia es mentiroso, dado que el verdadero esta en el HTML y no en el RSS.
      result, last_modified = read_clean(httpurl, clean=False, use_cache=use_cache)
      result = result.decode('utf-8')

      # HACKO el DIA:
      if url.startswith('farmacia://') or url.startswith('cartelera://') and apps_id[appid] == 'eldia':
        now = date2iso(datetime.now()+timedelta(hours=-3))
        result = re.sub(ur'\r?\n', u'</br>', result)
        result = u"""<rss xmlns:atom="http://www.w3.org/2005/Atom" 
                      xmlns:media="http://search.yahoo.com/mrss/" 
                      xmlns:news="http://www.diariosmoviles.com.ar/news-rss/" 
                      version="2.0" encoding="UTF-8"><channel>
                      <pubDate>%s</pubDate><item><![CDATA[%s]]></item></channel></rss>""" % (now, result)
    
    if type(result) != type(unicode()):
      result = result.decode('utf-8')

    result = (result, None, last_modified)
    set_cache(inner_url, result, mem_only=True)

  return result[0], result[2]

class HtmlBuilderMixing(object):
  
  def re_build_html_and_images(self, appid, url, size, ptls):
    
    inner_url = build_inner_url('html', appid, url, size)
    drop_cache(inner_url)

    return self.build_html_and_images(appid, url, size, ptls, use_cache=False)


  def build_html_and_images(self, appid, url, size, ptls, use_cache=True):
    # use_cache=False #HACK    
    try: 
      inner_url = build_inner_url('html', appid, url, size)

      result = None
      if use_cache:
        result = read_cache(inner_url)

      if result is None:
        # Traemos el xml, le quitamos los namespaces 
        xml, last_modified = get_xml(appid, url, use_cache=use_cache)
        xml = re.sub(r'<(/?)\w+:(\w+/?)', r'<\1\2', xml)
        
        #logging.error('---------*--------'+xml)
        # Y lo transformamos en un dict
        r = XML2Dict().fromstring(xml.encode('utf-8'))

        # Reemplazamos las imagens por el sha1 de la url
        imgs = []
        items = []
  
        if 'item' in r.rss.channel:
          if type(r.rss.channel.item) == OODict:
            items = [r.rss.channel.item]
          else:
            items = r.rss.channel.item

        for i in items:

          if hasattr(i, 'thumbnail'):
            img = unicode(i.thumbnail.attrs.url)

            i.thumbnail.attrs.url = sha1(img).digest().encode('hex') 
            #i.thumbnail.attrs.url = img #HACK
            
            imgs.append(img)

          if hasattr(i, 'group'):
            for ct in i.group.content:
              img = unicode(ct.attrs.url)
              ct.attrs.url = sha1(img).digest().encode('hex')
              imgs.append(img)

        if 'item' in r.rss.channel and not 'content' in r.rss.channel.item and type(r.rss.channel.item) != type([]):
          r.rss.channel.item = [r.rss.channel.item]

        # Armamos la direccion del xml    
        httpurl, args, template, page_name, extras_map = get_httpurl(appid, url, size, ptls)

        args = {'data': r.rss.channel, 'cfg': extras_map, 'page_name': page_name, 'raw_url':url , 'appid': apps_id[appid]}
        content = self.render_template('ws/%s' % template, **args)

        result = (content, u','.join(imgs), last_modified)
        set_cache(inner_url, result, mem_only=False)

      imgs = result[1].split(',') if result[1] else []
      #logging.error(result[0])
      return result[0], imgs, result[2]

    except Exception as e:
        import sys
        mymsg = 'build_html_and_images => %s %s %s %s %s => ' % (appid, url, size, ptls, use_cache)
        logging.error(mymsg)
        # xx = type(e)
        # xx.message = mymsg + e.message
        raise type(e), e, sys.exc_info()[2]
    
class Jinja2Mixin(object):
  
  @cached_property
  def jinja2(self):
    j2 = jinja2.get_jinja2(app=self.app)
      
    self.setup_jinja_enviroment(j2.environment)
      
    # Returns a Jinja2 renderer cached in the app registry.
    return j2

  def setup_jinja_enviroment(self, env):
    env.globals['url_for'] = self.uri_for
    
    if hasattr(self, 'session'):
      env.globals['session'] = self.session

      if hasattr(self.session, 'get_flashes'):
        flashes = self.session.get_flashes()
        env.globals['flash'] = flashes[0][0] if len(flashes) and len(flashes[0]) else None
    
    env.filters['urlencode']    = url_fix
    env.filters['datetime']     = format_datetime
    env.filters['noticia_link'] = noticia_link
    env.filters['if_not_none']  = if_not_none
    env.filters['has_content']  = has_content
    env.filters['content']      = get_content
    env.filters['gallery']      = gallery
    env.filters['meta_has']     = meta_has
    env.filters['related_link'] = related_link
    env.filters['build_list']   = build_list
    env.filters['is_empty']     = empty
    
          
  def render_response(self, _template, **context):
    # Renders a template and writes the result to the response.
    rv = self.jinja2.render_template(_template, **context)
    self.response.write(rv)
  
  def render_template(self, _template, **context):
    # Renders a template and writes the result to the response.
    rv = self.jinja2.render_template(_template, **context)
    return rv
      
class MyBaseHandler(RequestHandler, Jinja2Mixin, FlashBuildMixin):
  def dispatch(self):
    # Get a session store for this request.
    self.session_store = sessions.get_store(request=self.request)

    try:
      # Dispatch the request.
      RequestHandler.dispatch(self)
    finally:
      # Save all sessions.
      self.session_store.save_sessions(self.response)

  @cached_property
  def session(self):
    # Returns a session using the default cookie key.
    return self.session_store.get_session()
  
  def render_json_response(self, *args, **kwargs):
    self.response.content_type = 'application/json'
    self.response.write(json.encode(*args, **kwargs))
    
  # def handle_exception(self, exception=None, debug=False):
  #   logging.exception(exception)
    
  #   text = 'Se ha producido un error en el servidor,<br/>intenta volver al inicio'
  #   code = 500
    
  #   if isinstance(exception,HTTPException):
  #     if exception.code == 404:
  #       text = u'La página solicitada no ha sido encontrada,<br/>intenta volver al inicio'
      
  #     code = exception.code
    
  #   self.render_response('error.html', code=code, text=text )
  #   self.response.status = str(code)+' '

  @cached_property
  def config(self):
    return get_app().config
    
class FrontendMixin(object):
  def do_fullversion(self):
    self.session['fullversion']                  = True
  def dont_fullversion(self):
    self.session['fullversion']                  = False
    
class FrontendHandler(MyBaseHandler, FrontendMixin):
  pass

