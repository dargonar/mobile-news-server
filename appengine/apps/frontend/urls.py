# -*- coding: utf-8 -*-
from webapp2 import Route
from webapp2_extras.routes import PathPrefixRoute

def get_rules():
    
    rules = [
      PathPrefixRoute('/demo/service', [
        Route('/',                        name='frontend/home',               handler='apps.frontend.home.Index'),
        Route('/fullversion',             name='frontend/home/fullversion',   handler='apps.frontend.home.Index:fullversion'),
        Route('/view/<article>',          name='frontend/article',            handler='apps.frontend.home.ViewArticle'),
        Route('/m/secciones',             name='frontend/secciones',          handler='apps.frontend.home.ListSecciones'),
        Route('/m/secciones/<category>',  name='frontend/secciones/category', handler='apps.frontend.home.Index:get_seccion_articles'),
        Route('/m/servicios',             name='frontend/servicios',          handler='apps.frontend.home.ListServicios'),
        Route('/m/clasificados',          name='frontend/clasificados',       handler='apps.frontend.home.ListClasificados'),
        Route('/m/clasificados/automotores',          name='frontend/clasificados/automotores',       handler='apps.frontend.home.ListClasificados:automotores'),
        Route('/m/suplementos',           name='frontend/suplementos',        handler='apps.frontend.home.ListSuplementos'),
        Route('/m/perfil',                name='frontend/perfil',             handler='apps.frontend.home.Profile'),
        Route('/diarios/csv',             name='frontend/csv',                handler='apps.frontend.home.DiariosCsv'),
      ]),
      
      PathPrefixRoute('/demo/service2', [
        Route('/2/',                        name='frontend2/home',               handler='apps.frontend.handlers.Index'),
        Route('/2/fullversion',             name='frontend2/home/fullversion',   handler='apps.frontend.handlers.Index:fullversion'),
        Route('/2/view/<article>',          name='frontend2/article',            handler='apps.frontend.handlers.ViewArticle'),
        Route('/2/m/secciones',             name='frontend2/secciones',          handler='apps.frontend.handlers.ListSecciones'),
        Route('/2/m/secciones/<category>',  name='frontend2/secciones/category', handler='apps.frontend.handlers.Index:get_seccion_articles'),
        
      ]),
      
      PathPrefixRoute('/demo/service3', [
        Route('/3/',                        name='frontend3/home',               handler='apps.frontend.handlers2.Index'),
        Route('/3/fullversion',             name='frontend3/home/fullversion',   handler='apps.frontend.handlers2.Index:fullversion'),
        Route('/3/view/<article>',          name='frontend3/article',            handler='apps.frontend.handlers2.ViewArticle'),
        Route('/3/m/secciones',             name='frontend3/secciones',          handler='apps.frontend.handlers2.ListSecciones'),
        Route('/3/m/secciones/<category>',  name='frontend3/secciones/category', handler='apps.frontend.handlers2.Index:get_seccion_articles'),
        
      ])
    ]
    
    return rules
