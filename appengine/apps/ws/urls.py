# -*- coding: utf-8 -*-
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute, NamePrefixRoute, HandlerPrefixRoute

def get_rules():
    
    rules = [
      
        PathPrefixRoute('/ws', [ NamePrefixRoute('ws-', [ HandlerPrefixRoute('apps.ws.ScreenController', [
          Route('/screen',    name='get_screen',    handler='.ScreenController:get_screen'),
          Route('/xml',       name='get_xml',       handler='.ScreenController:get_xml'),
          Route('/html',      name='get_html',      handler='.ScreenController:get_html'),
          Route('/test',      name='test',          handler='.ScreenController:test'),
        ]) ]) ]),

    ]
    
    return rules
