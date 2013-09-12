# -*- coding: utf-8 -*-
from webapp2 import Route

def get_rules():
    
    rules = [
      Route('/download/article'         ,  name='backend/download_article'    , handler='apps.backend.download.DownloadAll:download_article'),
      Route('/download/section'         ,  name='backend/download_section'    , handler='apps.backend.download.DownloadAll:download_section'),
      Route('/download/newspaper'       ,  name='backend/download_newspaper'  , handler='apps.backend.download.DownloadAll:download_newspaper'),
      
      Route('/download/all'             ,  name='backend/download_all'        , handler='apps.backend.download.DownloadAll:download_all'),
      Route('/download/one/<newspaper>' ,  name='backend/download_one'        , handler='apps.backend.download.DownloadAll:download_one'),
      
      Route('/download/extras'          ,  name='backend/download_extras'     , handler='apps.backend.download.DownloadAll:download_extras'),
      Route('/download/clasificados'    ,  name='backend/download_claisf'     , handler='apps.backend.download.DownloadAll:download_clasificados'),
      Route('/download/page'            ,  name='backend/download_page'       , handler='apps.backend.download.DownloadAll:download_page'),
      
   #    Route('/download/eldia'   ,  name='backend/download'        , handler='apps.backend.download.ElDia:download'),
   #    Route('/download/feed'    ,  name='backend/download_feed'   , handler='apps.backend.download.ElDia:download_feed'),
   #    Route('/download/article' ,  name='backend/download_article', handler='apps.backend.download.ElDia:download_article'),
      
   #    Route('/download/ivc'         ,  name='backend/ivc/download'        , handler='apps.backend.download.IVC:download'),
			# Route('/download/ivc/feed'    ,  name='backend/ivc/download_feed'   , handler='apps.backend.download.IVC:download_feed'),
   #    Route('/download/ivc/article' ,  name='backend/ivc/download_article', handler='apps.backend.download.IVC:download_article'),
      
   #    Route('/list/ivc'         		,  name='backend/ivc/list'        		, handler='apps.backend.download.IVCViewer:list'),
      
   #    Route('/check/eldia_gallery'         ,  name='backend/eldia_gallery/download'        , handler='apps.backend.download.ElDiaRSS:download'),
   #    Route('/check/eldia_gallery/feed'    ,  name='backend/eldia_gallery/download_feed'   , handler='apps.backend.download.ElDiaRSS:download_feed'),
      #Route('/check/eldia_gallery/article' ,  name='backend/eldia_gallery/download_article', handler='apps.backend.download.ElDiaRSS:download_article'),
    ]
    
    return rules
