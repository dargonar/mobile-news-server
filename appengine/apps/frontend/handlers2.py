# -*- coding: utf-8 -*-
import logging

from google.appengine.ext import db

from models import Article, Category, cats, DiarioIVC
from utils import FrontendHandler, get_or_404

class Index(FrontendHandler):
  page_count = 20
  def get(self, **kwargs):
    self.dont_fullversion()
    return self.build_response(**kwargs)
  
  def fullversion(self, **kwargs):
    self.do_fullversion()
    self.session['page']='home'
    return self.build_response(**kwargs)
    
  def get_seccion_articles(self, **kwargs):
    self.session['page']='secciones'
    return self.build_response(**kwargs)
    
  def build_response(self, **kwargs):
    
    this_cursor = self.request.GET.get('more_cursor', None)
    
    if this_cursor is not None and len(str(this_cursor))<1:
      this_cursor=None
      
    query = Article.all()
    
    cats_conf=(dict((cat['key'], cat['desc']) for cat in cats))
    
    the_category = None
    category=None
    if kwargs.get('category', None) is not None:
      category=kwargs['category']
      _category = db.Key.from_path('Category',category)
      query.filter('category', _category)
      the_category = cats_conf[category]
      
    if this_cursor is not None:
      query.with_cursor(this_cursor)
    
    catitems = query.order('-published').fetch(self.page_count)
    
    more_cursor=''
    if len(catitems) == self.page_count:
      more_cursor = query.cursor()
  
    if this_cursor is not None:
      html    = self.render_template('new_frontend_emi/_articles.html', catitems=catitems, cats_conf=cats_conf)
      return self.render_json_response({
          'html': html,
          'more_cursor': more_cursor})
          
    return self.render_response('new_frontend_emi/_home.html', catitems=catitems, cats_conf=cats_conf, the_category=the_category, the_category_id=category, this_cursor=this_cursor, more_cursor = more_cursor )
  
  
class ViewArticle(FrontendHandler):
  def get(self, **kwargs):
    article = get_or_404(kwargs['article'])
    rel_articles = []
    if len(article.rel_art_keys)>0:
      for key in article.rel_art_keys:
        rel_articles.append( db.get(db.Key.from_path('Article',key)))
    #else:
      #local
      #rel_articles.append( db.get('ahBkZXZ-dGVzdHNkYXZlbnRvcjULEgdBcnRpY2xlIig5OGU1MDJjMzA2MTJjMzNhNjMwYjJmN2M3NzE3ZTA3ZTY3N2U5MzcyDA'))
      #rel_articles.append( db.get('ahBkZXZ-dGVzdHNkYXZlbnRvcjULEgdBcnRpY2xlIihjMzgyZjNlMjVjODRlNjMxMWFmODNjNzE5YWE2ZjBiZDkyMmU2YTM4DA'))
      #server
      #rel_articles.append( db.get('ag5zfnRlc3RzZGF2ZW50b3I1CxIHQXJ0aWNsZSIoYzlmMWMwMWUwNWVkMGU5MzBmYTU2NTlmNjBjYTg4ZmMyZDE4MmIzNgw'))
      #rel_articles.append( db.get('ag5zfnRlc3RzZGF2ZW50b3I1CxIHQXJ0aWNsZSIoMWEyMWFjMzhlZDViNWQ4YTI1ZTFhM2MzNDFmOWNhY2Q3Y2I0MTE2ZAw'))
      
    #self.session['page']='home'
    return self.render_response('new_frontend_emi/_article.html', article=article, rel_articles = rel_articles , cats_conf=(dict((cat['key'], cat['desc']) for cat in cats)))

class ListSecciones(FrontendHandler):
  def get(self, **kwargs):
    self.session['page']='secciones'
    return self.render_response('new_frontend_emi/_secciones.html', cats=cats)
