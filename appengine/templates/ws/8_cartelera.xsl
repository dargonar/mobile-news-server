{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout') }}
  <body onload="onLoad('{{page_name}}')" class="{{appid}}">
    <div id="clasificados">
      <div class="columna">
        <div class="encabezado">
          <div class="rubro">Cartelera de cine</div>
          <div class="clear"></div>
          <div class="titulo"></div>
          {{ cc.DayMonthYear(data) }}
          <div class="clear"></div>
        </div>
        
        <div class="aviso" id="farmacia_list">
        {{data.item}}
        </div>
      </div>
    </div>
  </body>
</html>