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
        <li><a class="vip2" href="{{cfg.has_clasificados}}">Clasificados</a></li>
        {% endif %}
        
        {% if cfg.has_funebres %}
        <li><a class="vip2" href="{{cfg.has_funebres}}">Fúnebres</a></li>
        {% endif %}

        {% if cfg.has_farmacia %}
        <li><a class="vip2" href="{{cfg.has_farmacia}}">Farmacias de turno</a></li>
        {% endif %}
        
        {% if cfg.has_cartelera %}
        <li><a class="vip2" href="{{cfg.has_cartelera}}">Cartelera de cine</a></li>
        {% endif %}

        <li class="vip2_close"></li>
      </ul>
    </div>

  </body>
</html>