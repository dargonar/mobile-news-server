# -*- coding: utf-8 -*-
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, NamePrefixRoute, HandlerPrefixRoute, DomainRoute

def get_rules():
    
    rules = [
    #   r'<domain:(^((?latincoin)[\s\S])*$)>'
    #   DomainRoute('latincoin.com.ar', [
      
      DomainRoute(r'www.latincoin.com.ar', [
        Route('/',                     name='mvp/latincoin',           handler='apps.mvp_1.handlers.Index:latincoin'),
      ]),

      Route('/',                        name='mvp/index',              handler='apps.mvp_1.handlers.Index'),
      Route('/demo',                    name='mvp/demo',               handler='apps.mvp_1.handlers.Index:demo'),
      Route('/solicitar_agente',        name='mvp/ask_for_agent',      handler='apps.mvp_1.handlers.Index:post'),
      Route('/<slug>',                  name='mvp/slug',               handler='apps.mvp_1.handlers.Index:slug'),
      Route('/mvp/sendmail',            name='mvp/sendmail',           handler='apps.mvp_1.handlers.SendMail'),
    ]
    
    return rules
