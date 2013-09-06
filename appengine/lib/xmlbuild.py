# -*- coding: utf-8 -*-
from StringIO import StringIO
import threading

def nb(item, key):
  if key in item and item[key].lower() in ['true', 'false']:
    return item[key].lower()
  return 'false'

def ns(item, key, v=''):
  if key in item:
    return item[key]
  return v

class XMLBuild():

  def __init__(self, conf, pubDate):
    self.conf     = conf
    self.pubDate  = pubDate.strftime("%a, %d %b %Y %H:%M:%S")
    self.finished = False
    self.funlock  = threading.Lock()

    self.out  = StringIO()
    self.out.write( self.get_header(self.conf, self.pubDate) )

  def write(self, content):
    self.out.write(u'\t%s\n' % content)

  def get_value(self):
    if self.finished == False:
      self.finished = True
      self.out.write( self.get_footer() )

    return self.out.getvalue()

  def get_header(self, conf, pubDate):  
    return u"""<?xml version="1.0" encoding="UTF-8" ?>
    <rss xmlns:atom="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/"
    xmlns:news="http://www.diariosmoviles.com.ar/news-rss/" version="2.0">
    <channel>
     <title>%s</title>
     <link>%s</link>
     <description>%s</description>
     <copyright>%s</copyright>
     <pubDate>%s</pubDate>
     <image>
       <title>%s - RSS</title>
       <url>%s</url>
       <link>%s</link>
     </image>
     <ttl>10</ttl>
     <atom:link href="%s/simu.rss" rel="self  " type="application/rss+xml"/>
    """ % ( ns(conf,'title'), ns(conf,'url'), ns(conf,'description'), ns(conf,'copyright'), pubDate, ns(conf,'title'), ns(conf,'logo'), ns(conf,'url'), ns(conf,'url'))

  def get_footer(self):
    return u"""
     </channel>
    </rss>
    """

  def add_raw(self, raw):
    self.write( u'<item><![CDATA[%s]]></item>' % raw )

  def add_common(self, item):
    self.write( u'<title><![CDATA[%s]]></title>' % ns(item,'title') )
    self.write( u'<description><![CDATA[%s]]></description>' % ns(item,'description') )
    self.write( u'<link><![CDATA[%s]]></link>' % ns(item,'link') )
    self.write( u'<guid isPermaLink="false"><![CDATA[%s]]></guid>' % ns(item,'guid') )
    self.write( u'<pubDate>%s</pubDate>' % ns(item, 'pubDate'))
    self.write( u'<author><![CDATA[%s]]></author>' % ns(item, 'author'))
    self.write( u'<category><![CDATA[%s]]></category>' % ns(item, 'category') )

  def add_content(self, item):
    
    self.write( u'<news:lead type="plain" meta="volanta"><![CDATA[%s]]></news:lead>' % ns(item,'lead') )
    self.write( u'<news:subheader type="plain" meta="bajada"><![CDATA[%s]]></news:subheader>' % ns(item,'subheader') )

    if item.get('thumbnail') is not None:
      self.write( u'<media:thumbnail url="%s"></media:thumbnail>' % item['thumbnail'] )
    
    if item.get('content') is not None:
      self.write( u'<news:content type="html" meta="contenido"><![CDATA[%s]]></news:content>' % ns(item,'content'))

    if item.get('group') is not None and len(item['group']):
      self.write( u'<media:group>')
      for img in item['group']:
        self.write( u'<media:content url="%s" type="image/jpeg"></media:content>' % img )
      self.write( u'</media:group>')      

    self.write( u'<news:meta has_gallery="%s" has_video="%s" has_audio="%s" />' % ( nb(item,'has_gallery'), nb(item, 'has_video'), nb(item, 'has_audio') ) )

  def add_item(self, item):    
    self.write( u'<item>')
    self.add_common(item)
    self.add_content(item)
    self.write( u'</item>')

  def add_section(self, item):
    self.write( u'<item>')
    self.add_common(item)
    self.write( u'</item>')

  def add_news(self, item):
    self.add(item)

  def add_funebre(self, item):
    with self.funlock:
      self.add_section(item)