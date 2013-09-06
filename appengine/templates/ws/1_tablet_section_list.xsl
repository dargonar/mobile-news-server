{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout_tablet') }}
  <body onload="onLoad('{{page_name}}')" class="{{appid}} portrait padded">
    {{ cc.UpdatedAt() }}
    <div id="index" class="padded_landscape top_padded">
      {{raw_url}}
      {{ cc.tablet_index_portrait_secondary(data.item[0:2], raw_url) }}
      {{ cc.tablet_index_portrait_terciary(data.item[2:], raw_url) }}
    </div>
  </body>
</html>