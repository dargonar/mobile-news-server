{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout_tablet') }}  
  <body onload="onLoad('{{page_name}}')" class="{{appid}}">
    <div id="clasificados">
      {% set items = data.item|build_list %}

      <div class="columna">
        <div class="encabezado">
          <div class="titulo">Clasificados</div>
          <div class="rubro">{{items.0.title}}</div>
          <p></p>
          {{ cc.DayMonthYear(items.0) }}
          <div class="clear"></div>
        </div>
        
        {{ cc.avisos_clasificados(items, columna=0) }}
      </div>
      
      <div class="columna">
        {{ cc.avisos_clasificados(items, columna=1) }}
      </div>
      
      <div class="columna">
        {{ cc.avisos_clasificados(items, columna=2) }}
      </div>
      
    </div><!-- clasificados -->
  </body>
</html>



