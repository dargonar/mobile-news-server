{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout_tablet') }}
  <body onload="onLoad('{{page_name}}')" class="menu {{appid}}">
    <div id="menu">
      <ul>
        <li class="seccion">Noticias</li>
        <li><a href="section://main">Principal</a></li>
        {% for item in data.item %}
        <li><a href="section://{{item.guid.value}}">{{item.title}}</a></li>
        {% endfor %}
       
        {% if cfg.has_clasificados %}
          {% if appid == 'ecosdiarios'%}
            <li class="seccion"> <a class="no_style" href="http://www.ecosdiariosweb.com.ar/clasificados/clasificados.pdf" >Clasificados</a></li>
          {% else %}
            <li class="seccion"> <a class="no_style" href="#" onclick="return toggle('ul_clasificados', 'invisible');" >Clasificados</a></li>
          {% endif %}
        {% endif %}
      </ul>
      {% if cfg.has_clasificados %} 
        {% if appid != 'ecosdiarios'%}
          <ul class="invisible" id="ul_clasificados">
            {% for id, desc in cfg.clasificados.iteritems() %}
            <li><a class="vip2" href="clasificados://{{id}}">{{desc}}</a></li>
            {% endfor %}
          </ul>
        {% endif %}
      {% endif %}

      {% if cfg.has_funebres or cfg.has_farmacia or cfg.has_cartelera %}      
      <ul>
        <li class="seccion"> <a class="no_style" href="#" onclick="return toggle('ul_varios', 'invisible');" >Servicios varios</a></li>
      </ul>
      <ul class="invisible" id="ul_varios">
        {% if cfg.has_funebres %}
        <li><a class="vip2" href="funebres://full">Fúnebres</a></li>
        {% endif %}

        {% if cfg.has_farmacia %}
          {% set inner_url = 'farmacia://full' %}
          {% set inner_url = 'http://circulorafaela.com.ar/farmacias.htm' if appid == 'castellanos' else 'farmacia://' %}
          
        <li><a class="vip2" href="{{inner_url}}">Farmacias de turno</a></li>
        {% endif %}

        {% if cfg.has_cartelera %}
          {% set inner_url = 'http://www.rafaela.gov.ar/cine/' if appid == 'castellanos' else 'cartelera://' %}
        <li><a class="vip2" href="{{inner_url}}">Cartelera de cine</a></li>
        {% endif %}
      </ul>
      {% endif %}

    </div>

  </body>
</html>