{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout') }}
  <body onload="onLoad('{{page_name}}')" class="{{appid}}">
    <div id="clasificados">
      <div class="columna">
        {% for item in data.item|build_list %}
          {% if loop.first %}
          <div class="encabezado">
            <div class="titulo">Cartelera</div>
            <!-- div class="rubro">
              
            </div -->
            <p></p>
            <div class="clear"></div>
          </div>
          {% endif %}
          <div class="rubro">{{item.category}}</div>
          <div class="cartelera_item"> <!-- aviso -->
            <p class="carte_title">{{item.title}}</p>
            <p class="carte_desc">{{item.content.value}}</p>
          </div>
        {% endfor %}
      </div>  
    </div>
 </body>
</html>