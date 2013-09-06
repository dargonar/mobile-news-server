{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout') }}
  <body onload="onLoad('{{page_name}}')" class="{{appid}}">
    {{ cc.UpdatedAt() }}
    {{ cc.DestacadaEnListadoPrincipal(data.item.0) }}
    {{ cc.ListadoNoticiasEnListado(data.item[1:]) }}
  </body>
</html>