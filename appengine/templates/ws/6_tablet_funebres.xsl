{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout_tablet') }}  
  <body onload="onLoad('{{page_name}}')" class="{{appid}}">
    <div id="clasificados">
      {% set items = data.item|build_list %}
      <div class="columna">
        <div class="encabezado">
          <div class="titulo">Fúnebres</div>
          <p></p>
          <div class="clear"></div>
        </div>
        
        {{ cc.avisos_funebres(items, columna=0) }}
      </div>
      
      <div class="columna">
        {{ cc.avisos_funebres(items, columna=1) }}
      </div>
      
      <div class="columna">
        {{ cc.avisos_funebres(items, columna=2) }}
      </div>
    </div>
  </body>
</html>