# -*- coding: utf-8 -*-
import logging

from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api import taskqueue

from webapp2 import cached_property

from models import RegisteredEditor
from forms import RegisteredEditorForm

from utils import FrontendHandler, get_or_404

class Index(FrontendHandler):
  def get(self, **kwargs):
    #return self.render_response('mvp_1/_index.html', form=self.form, **kwargs)
    return self.render_response('mvp_1/_index.html', form=self.form, **kwargs)
  
  def demo(self, **kwargs):
    return self.render_response('mvp_1/_demo.html')
    
  def slug(self, **kwargs):
    if kwargs['slug'] not in ['que_hacemos', 'faq', 'diarios' , 'contacto']:
      return self.redirect_to('mvp/index')
    kwargs['go_to']=kwargs['slug']
    return self.render_response('mvp_1/_index.html', form=self.form, **kwargs)

  def post(self, **kwargs):
    self.request.charset  = 'utf-8'
    
    if not self.form.validate():
      str_error = u'Verifique los datos ingresados'
      #str_error = u'Verifique los datos ingresados:<br/><span></span>' + '<br/><span></span>'.join(reduce(lambda x, y: str(x)+' '+str(y), t) for t in self.form.errors.values())
      self.set_error(str_error)
      return self.render_response('mvp_1/_index.html', form=self.form)
      #return self.redirect_to('mvp/index', **self.form.data)
    
    mUser             = RegisteredEditor()
    self.form.update_object(mUser)
    mUser.put()
    
    self.set_ok(u'Solicitud confirmada.<br/> Un agente se contactará con Usted a la brevedad.')
    
    taskqueue.add(url='/mvp/sendmail', params={'editor':mUser.name, 'email':mUser.email, 'data': ' key:[%s]; fullname:[%s] www:[%s]' % (str(mUser.key()), mUser.name, mUser.website)})
                 
    return self.redirect_to('mvp/index')
      
  @cached_property
  def form(self):
    return RegisteredEditorForm(self.request.params)
  
class SendMail(FrontendHandler):
  def post(self, **kwargs):
    self.request.charset = 'utf-8'
    
    data = self.request.POST.get('data')
    editor = self.request.POST.get('editor')
    email = self.request.POST.get('email')
    
    sender = 'info@diariosmoviles.com.ar'
    
    mail.send_mail(sender="DiariosMoviles <%s>" % sender, 
                 to       = 'pablo.tutino@gmail.com, matias.romeo@gmail.com',
                 subject  = 'Un nuevo editor se ha registrado',
                 body     = data)
    
    
    body = self.render_template('email/welcome.txt', editor=editor)  
    html = self.render_template('email/welcome.html', editor=editor)  
    
    # Envío el correo.
    mail.send_mail(sender="DiariosMoviles <%s>" % sender, 
                 to       = email,
                 subject  = u'Bienvenido a Diarios Móviles',
                 body     = body,
                 html     = html)