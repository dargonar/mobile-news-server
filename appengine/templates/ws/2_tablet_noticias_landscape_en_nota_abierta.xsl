{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout_tablet') }}
  <body class="{{appid}} landscape" onload="onLoad('{{page_name}}')">
    <div id="landscape">
      <div class="seccion list">{{'Principal' if '://main' in page_name else data.item.0.category }}</div>
      <div class="menu">
        <ul class="landscape_news_list">
        {{ cc.tablet_news_list_landscape(data.item, raw_url) }}
        </ul>
      </div>
    </div>
  </body>
</html>