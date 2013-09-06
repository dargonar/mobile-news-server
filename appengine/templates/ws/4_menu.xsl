{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout') }}
  <body class="menu {{appid}}" style="margin:0;" onload="onLoad('{{page_name}}')">
    <div id="menu">
      <div class="menu-header">Secciones</div>
      <ul>
        <li><a href="section://main">Principal</a></li>
        {% for item in data.item %}
        <li><a href="section://{{item.guid.value}}">{{item.title}}</a></li>
        {% endfor %}
        
        {% if cfg.has_clasificados %}
          {% set inner_url = 'http://www.ecosdiariosweb.com.ar/clasificados/clasificados.pdf' if appid == 'ecosdiarios' else 'clasificados://list' %}
         
        <li><a class="vip2" href="{{inner_url}}">Clasificados</a></li>
        {% endif %}
        
        {% if cfg.has_funebres %}
          {% set inner_url = 'funebres://' %}
          
        <li><a class="vip2" href="{{inner_url}}">Fúnebres</a></li>
        {% endif %}

        {% if cfg.has_farmacia %}
          {% set inner_url = 'http://circulorafaela.com.ar/farmacias.htm' if appid == 'castellanos' else 'farmacia://' %}
          
        <li><a class="vip2" href="{{inner_url}}">Farmacias de turno</a></li>
        {% endif %}
        
        {% if cfg.has_cartelera %}
          {% set inner_url = 'http://www.rafaela.gov.ar/cine/' if appid == 'castellanos' else 'cartelera://' %}
          
        <li><a class="vip2" href="{{inner_url}}">Cartelera de cine</a></li>
        {% endif %}

        <li class="vip2_close"></li>
      </ul>
    </div>

  </body>
</html>