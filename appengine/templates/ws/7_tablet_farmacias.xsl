{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout_tablet') }}
  <body onload="onLoad('{{page_name}}')" class="{{appid}}">
    <div id="clasificados">
      <div class="columna big">
        <div class="encabezado">
          <div class="rubro">Farmacias de turno</div>
          <div class="clear"></div>
          <div class="titulo"></div>
          {{ cc.DayMonthYear(data) }}
          <div class="clear"></div>
        </div>

        <div class="aviso two_columns" id="farmacia_list">
        {{data.item}}
        </div>
      </div>  
    </div>
  </body>
</html>