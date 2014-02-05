{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout') }}
  <body onload="onLoad('{{page_name}}')" class="{{appid}}">
    <div id="titulo_seccion">
      {% if page_name == 'section://columnistas'%}
        <label class="lbl_titulo_seccion">Columnistas</label>
      {% else %}
        {% if data and data.item|length>0 %}
          {% if appid == 'ecosdiarios'%}
            <label class="lbl_titulo_seccion">{{data.item.0.description}}</label>
          {% else %}
            <label class="lbl_titulo_seccion">{{data.item.0.category}}</label>
          {% endif %}
        {% else %}
          <label class="lbl_titulo_seccion">No hay noticias</label>
        {% endif %}
      {% endif %}
    </div>
    {{ cc.UpdatedAt() }}
    {{ cc.ListadoNoticiasEnListado(data.item) }}
  </body>
</html>
