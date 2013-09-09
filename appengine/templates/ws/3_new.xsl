{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout') }}
  <body onload="onLoad('{{page_name}}')" class="{{appid}}">
    <div class="nota_abierta">
      {{ cc.NotaAbierta(data.item) }}
    </div>
    {% if data.item.related %}
      {{ cc.TituloSeccionONotisRelac('Noticias relacionadas') }}
      {{ cc.ListadoNoticiasRelacionadas(data.item.related|build_list) }}
    {% endif %}
  </body>
</html>