{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout') }}
  <body onload="onLoad('{{page_name}}')" class="{{appid}}">
    {{ cc.NotaAbierta(data.item) }}

    {% if data.item.related %}
      {{ cc.TituloSeccionONotisRelac('Noticias relacionadas') }}
      {{ cc.ListadoNoticiasRelacionadas(data.item.related|build_list) }}
    {% endif %}
  </body>
</html>