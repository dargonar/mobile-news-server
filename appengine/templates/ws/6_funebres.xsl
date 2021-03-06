{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout') }}  
  <body onload="onLoad('{{page_name}}')" class="{{appid}}">
    <div id="clasificados">
      <div class="columna">
        <div class="encabezado">
          <div class="titulo">Funebres</div>
          <p></p>
          <div class="clear"></div>
        </div>
        {% set last_cat = '' %}
        {% for item in data.item|build_list %}
        {% if not loop.last %}
        
        {% if last_cat != item.category %}
        <div class="rubro">{{item.category}}</div>
        {% set last_cat = item.category %}
        {% endif %}
        <div class="aviso">
          {% if item.title and item.title|length>0%}
            <p>{{item.title}}</p>
          {% endif %}
          <p>{{item.description|if_not_none}}</p> 
        </div>

        {% endif %}
        {% endfor %}
      </div>  
    </div>
  </body>
</html>