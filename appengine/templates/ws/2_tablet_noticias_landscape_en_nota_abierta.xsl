{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout_tablet') }}
  <body class="{{appid}} landscape" onload="onLoad('{{page_name}}')">
    <div id="landscape">
      {% if 'section://columnistas' in raw_url%}
        <div class="seccion list">Columnistas</div>
      {% else %}
        <div class="seccion list">{{'Principal' if 'section://main' in raw_url else data.item.0.category }}</div>
      {% endif %}
      <div class="menu">
        <ul class="landscape_news_list">
        {{ cc.tablet_news_list_landscape(data.item, raw_url) }}
        </ul>
      </div>
    </div>
  </body>
</html>