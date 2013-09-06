# -*- coding: utf-8 -*-
from collections import OrderedDict
from datetime import datetime
from xmlbuild import XMLBuild

conf = {  'title'       : u'EL DIA',
          'url'         : u'http://www.eldia.com.ar',
          'description' : u'EL DIA',
          'copyright'   : u'2013, El Dia',
          'logo'        : u'http://www.eldia.com.ar/imag/logo.png' }

def rss_clasificados(args):

  builder = XMLBuild(conf, datetime.now())
  
  for _id, title in get_classifieds().items():
    item = {}
    item['title'] = title
    item['link']  = 'clasificados://%s' % _id
    item['guid']  = _id

    builder.add_item(item)

  return builder.get_value()


def get_classifieds():
  return OrderedDict([
  ('0', u'Salud'),
  ('1', u'Alquiler de habitaciones'),
  ('2', u'Alquiler de inmuebles'),
  ('3', u'Geriátricos y pensiones'),
  ('4', u'Compra y venta de inmuebles'),
  ('5', u'Compra venta y alquiler de neg. ped. socios'),
  ('6', u'Veterinarias, mascotas'),
  ('7', u'Compra y venta de automotores'),
  ('8', u'Compra y venta de motos y accesorios'),
  ('9', u'Transportes'),
  ('10', u'Compra y venta art. del hogar (usados)'),
  ('11', u'Electrónica, música, equipos  y fotografía'),
  ('12', u'Construccio-nes, planos y empresas'),
  ('13', u'Albañilería, pintura, plomería, rep. techos'),
  ('14', u'Hipotecas, prestamos, transferencias y seguros'),
  ('15', u'Festejos y guarderías'),
  ('16', u'Enseñanza de idiomas y traducciones'),
  ('17', u'Enseñanza particular'),
  ('18', u'Máquinas de coser, tejer, escribir y calcular'),
  ('19', u'Materiales de construcción'),
  ('20', u'Modistas, sastres, talleres, arreglos ropa'),
  ('21', u'Oficios ofrecidos'),
  ('22', u'Empleos'),
  ('23', u'Tarot - astrología - parapsicología'),
  ('24', u'Extravios y hallazgos'),
  ('25', u'Personas buscadas'),
  ('26', u'Personal casa flia. ofrecidos'),
  ('27', u'Personal casa flia. pedidos'),
  ('28', u'Service de art. del hogar reparaciones'),
  ('29', u'Varios'),
  ('30', u'Art. suntuarios, alhajas, oro'),
  ('31', u'Cursos varios'),
  ('32', u'Deportes y camping'),
  ('33', u'Remates, demoliciones'),
  ('34', u'Jardinería, plantas y viveros'),
  ('35', u'Carpintería metalica y madera, puertas, cortinas'),
  ('36', u'Ferreterías - cerrajerías')
  ])

def get_mapping():
  return {
    'map':
    OrderedDict([
      ('section://main' , {
        'url'    : 'http://www.eldia.com.ar/rss/index.aspx',
        'small'  : {'pt': '1_main_list.xsl',              'ls': '1_main_list.xsl'},
        'big'    : {'pt': '1_tablet_main_list.xsl',       'ls': '1_tablet_main_list.xsl'},
      }),
      
      ('noticia://' , {
        'url'    : 'http://www.eldia.com.ar/rss/noticia.aspx?id=%s',
        'small'  : {'pt': '3_new.xsl',                    'ls': '3_new.xsl'},
        'big'    : {'pt': '3_tablet_new_global.xsl',      'ls': '3_tablet_new_global.xsl'},
      }),

      ('section://' , {
        'url'    : 'http://www.eldia.com.ar/rss/index.aspx?seccion=%s',
        'small'  : {'pt': '2_section_list.xsl',           'ls': '2_section_list.xsl'},
        'big'    : {'pt': '1_tablet_section_list.xsl',    'ls': '1_tablet_section_list.xsl'},
      }),

      ('menu://' , {
        'url'    : 'http://www.eldia.com.ar/rss/secciones.aspx',
        'small'  : {'pt': '4_menu.xsl',                   'ls': '4_menu.xsl'},
        'big'    : {'pt': '4_tablet_menu_secciones.xsl',  'ls': '4_tablet_menu_secciones.xsl'},
      }),
  
      ('funebres://' , {
        'url'    : 'http://www.eldia.com.ar/mc/fune_rss_utf8.aspx',
        'small'  : {'pt': '6_funebres.xsl',               'ls': '6_funebres.xsl'},
        'big'    : {'pt': '6_tablet_funebres.xsl',        'ls': '6_tablet_funebres.xsl'},
      }),

      ('menu_section://main' , {
        'url'    : 'http://www.eldia.com.ar/rss/index.aspx',
        'small'  : None,
        'big'    : {'pt': '2_tablet_noticias_portrait_en_nota_abierta.xsl',  'ls': '2_tablet_noticias_portrait_en_nota_abierta.xsl'},
      }),

      ('ls_menu_section://main' , {
        'url'    : 'http://www.eldia.com.ar/rss/index.aspx',
        'small'  : None,
        'big'    : {'pt': '2_tablet_noticias_landscape_en_nota_abierta.xsl',  'ls': '2_tablet_noticias_landscape_en_nota_abierta.xsl'},
      }),

      ('menu_section://' , {
        'url'    : 'http://www.eldia.com.ar/rss/index.aspx?seccion=%s',
        'small'  : None,
        'big'    : {'pt': '2_tablet_noticias_portrait_en_nota_abierta.xsl',  'ls': '2_tablet_noticias_portrait_en_nota_abierta.xsl'},
      }),

      ('ls_menu_section://' , {
        'url'    : 'http://www.eldia.com.ar/rss/index.aspx?seccion=%s',
        'small'  : None,
        'big'    : {'pt': '2_tablet_noticias_landscape_en_nota_abierta.xsl',  'ls': '2_tablet_noticias_landscape_en_nota_abierta.xsl'},
      }),
      
     ('clasificados://list' , {
        'url'    : 'X: rss_clasificados',
        'small'  : {'pt': '9_menu_clasificados.xsl', 'ls': '9_menu_clasificados.xsl'},
        'big'    : None
      }),
      
     ('clasificados://' , {
        'url'    : 'http://www.eldia.com.ar/mc/clasi_rss_utf8.aspx?idr=%s&app=1',
        'small'  : {'pt': '5_clasificados.xsl', 'ls': '5_clasificados.xsl'},
        'big'    : {'pt': '5_tablet_clasificados.xsl', 'ls': '5_tablet_clasificados.xsl'}
      }),
      
      ('farmacia://' , {
        'url'    : 'http://www.eldia.com.ar/extras/farmacias_txt.aspx',
        'small'  : {'pt': '7_farmacias.xsl',        'ls': '7_farmacias.xsl'},
        'big'    : {'pt': '7_tablet_farmacias.xsl', 'ls': '7_tablet_farmacias.xsl'},
      }),
      
      ('cartelera://' , {
        'url'    : 'http://www.eldia.com.ar/extras/carteleradecine_txt.aspx',
        'small'  : {'pt': '8_cartelera.xsl',        'ls': '8_cartelera.xsl'},
        'big'    : {'pt': '8_tablet_cartelera.xsl', 'ls': '8_tablet_cartelera.xsl'}
      }),
    ]),
    'extras': {
      'has_clasificados' : True,
      'has_funebres'     : True,
      'has_farmacia'     : True,
      'has_cartelera'    : True,
    },
    'config': {
        'android': { 'ad_mob': 'a1521debeb75556', 'google_analytics' : ['UA-32663760-2'] },
        'iphone':  { 'ad_mob': 'a1521debeb75556', 'google_analytics' : ['UA-32663760-2'] },
        'ipad':    { 'ad_mob': 'a1521debeb75556', 'google_analytics' : ['UA-32663760-2'] }
    }
  } 