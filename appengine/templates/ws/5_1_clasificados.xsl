{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout') }}
  <body onload="onLoad('{{page_name}}')" class="{{appid}}">
    <div id="clasificados">
      <div class="columna">
        {% set cat = '' %}
        {% for item in data.item|build_list %}
        {% if loop.first %}
        <div class="encabezado">
          <div class="titulo">{{page_name|replace('clasificados://','')}}</div>
          <!--div class="rubro">
            {{item.title}}
          </div-->
          <p></p>
          <div class="clear"></div>
        </div>
        {% endif %}
        {% if cat != item.category %}
          <div class="rubroex">{{item.category}}</div>
          {% set cat = item.category %}
        {% endif %}
        <div class="aviso"> <!-- aviso -->
          <p><b>{{item.title}}</b></p>
          <p>{{item.description}}</p>
        </div>
        {% endfor %}
      </div>  
    </div>
 </body>
</html>