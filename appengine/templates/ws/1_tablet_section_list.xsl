{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout_tablet') }}
  <body onload="onLoad('{{page_name}}')" class="{{appid}} portrait padded">
    {{ cc.UpdatedAt() }}
    <div id="index" class="padded_landscape top_padded">
      {% if data and data.item|length>0 %}
        {% set secondary_len = 2 if data.item|length>=3 else data.item|length-1 %}
        {{ cc.tablet_index_portrait_secondary(data.item[0:2], raw_url) }}
        {% if data and data.item|length>3 %}
          {{ cc.tablet_index_portrait_terciary(data.item[2:], raw_url) }}
        {% endif %}
      {% endif %}
    </div>
  </body>
</html>