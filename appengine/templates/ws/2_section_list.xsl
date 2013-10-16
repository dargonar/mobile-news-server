{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout') }}
  <body onload="onLoad('{{page_name}}')" class="{{appid}}">
    <div id="titulo_seccion">
      {% if page_name == 'section://columnistas'%}
        <label class="lbl_titulo_seccion">Columnistas</label>
      {% else %}
        <label class="lbl_titulo_seccion">{{data.item.0.category}}</label>
      {% endif %}
    </div>
    {{ cc.UpdatedAt() }}
    {{ cc.ListadoNoticiasEnListado(data.item) }}
  </body>
</html>
