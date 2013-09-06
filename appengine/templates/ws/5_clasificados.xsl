{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout') }}
  <body onload="onLoad('{{page_name}}')" class="{{appid}}">
    <div id="clasificados">
      <div class="columna">
        {% for item in data.item|build_list %}
        {% if loop.first %}
        <div class="encabezado">
          <div class="titulo">Clasificados</div>
          <div class="rubro">
            {{item.title}}
          </div>
          <p></p>
          <div class="clear"></div>
        </div>
        {% endif %}
        {% if not loop.last %}
        <div class="aviso"> <p>{{item.description}}</p></div>
        {% endif %}
        {% endfor %}
      </div>  
    </div>
 </body>
</html>