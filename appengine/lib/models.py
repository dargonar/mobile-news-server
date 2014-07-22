# -*- coding: utf-8 -*-
import logging

from google.appengine.ext import db, blobstore
from google.appengine.api.images import get_serving_url

from datetime import date, datetime , timedelta

class CachedContent(db.Model):
  content            = db.TextProperty()
  images             = db.TextProperty()
  appid              = db.StringProperty()
  url_type           = db.StringProperty()
  inner_url          = db.StringProperty()
  last_modified      = db.StringProperty()
  created_at         = db.DateTimeProperty(auto_now_add=True)

class RegisteredEditor(db.Model):
  created_at         = db.DateTimeProperty(auto_now_add=True)
  name               = db.StringProperty(indexed=False)
  email              = db.EmailProperty()
  telephone          = db.StringProperty(indexed=False)
  mobile             = db.StringProperty(indexed=False)
  call_at            = db.StringProperty(indexed=False)
  message            = db.StringProperty(indexed=False)
  website            = db.StringProperty(indexed=False)
  
  def __repr__(self):
    return 'RegisteredEditor: ' + self.email
