{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout_tablet') }}
  <body onload="onLoad('{{page_name}}')" class="portrait padded global {{appid}}">
  {{ cc.tablet_open_new_global(data.item) }}
  </body>
</html>