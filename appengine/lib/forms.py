# -*- coding: utf-8 -*-
"""
    backend forms
    ~~~~~~~~
"""
import re
import logging

from wtforms import Form, BooleanField, SelectField, TextField, FloatField , PasswordField, FileField, DateField
from wtforms import HiddenField, TextAreaField, IntegerField, validators, ValidationError
from wtforms.widgets import TextInput
from wtforms.ext.appengine.fields import GeoPtPropertyField
from wtforms.validators import regexp
from google.appengine.ext import db

from models import RegisteredEditor

def is_number(s):
  try:
    float(s)
    return True
  except:
    return False

def is_int(s):
  try:
    int(s)
    return True
  except:
    return False
    
def to_float(val):
  try:
    return float(val)
  except:
    return 0.0

def to_int(val):
  try:
    return int(val)
  except:
    return 0
  
def my_float_validator(field, condition):
  if condition:
    if not field.data or isinstance(field.data, basestring) and not field.data.strip():
      raise ValidationError('Debe ingresar un precio')
    if not is_number(field.data):
      raise ValidationError('El precio es invalido')

def my_float_validator_simple(field):
  if field.data.strip() != '' and not is_number(field.data):
    raise ValidationError('El precio es invalido')
      
def my_int_validator(field):
  if field.data.strip() != '' and not is_int(field.data):
    raise ValidationError('El numero es invalido')



class RegisteredEditorForm(Form):
  def __repr__(self):
    return 'RegisteredEditorForm'
  # Attributes
  name                = TextField('',[validators.Required(message=u'Debe ingresar nombre y apellido.')])
  email               = TextField('',[validators.email(message=u'Debe ingresar un correo válido.')
                                      , validators.Required(message=u'Debe ingresar un correo electrónico.')], default='')
  
  website             = TextField('', default='')
  
  telephone           = TextField('',[validators.Required(message=u'Debe ingresar un número de teléfono.')])
  mobile              = TextField('')
  call_at             = TextField('') #SelectField('Moneda',choices=[('ARS', '$ - Pesos'), ('USD', 'USD - Dolares')],default='ARS') #TextField('')
  message             = TextAreaField('', default='')
  
  def update_object(self, rs):
    rs.name               = self.name.data
    rs.email              = self.email.data
    rs.telephone          = self.telephone.data
    rs.mobile             = self.mobile.data
    rs.call_at            = self.call_at.data
    rs.message            = self.message.data
    rs.website            = self.website.data
    
    return rs
  
  def validate_website(form, field):
    
    if field.data.strip() == '':
      return
    
    tld_part = ur'\.[a-z]{2,10}'
    if 'http://' in field.data:
      regex = ur'^[a-z]+://([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})(:[0-9]+)?(\/.*)?$' % tld_part
      mRegexp = regexp(regex, re.IGNORECASE, message=u'URL inválida.')
    else:
      regex = ur'([^/:]+%s|([0-9]{1,3}\.){3}[0-9]{1,3})(:[0-9]+)?(\/.*)?$' % tld_part
      mRegexp = regexp(regex, re.IGNORECASE, message=u'URL inválida.')
    mRegexp.__call__(form, field)
    
  def validate_email(form, field):
    user        = RegisteredEditor.all().filter('email =', field.data).get()
    
    if user:
      raise ValidationError(u'Este correo ya ha sido registrado.')