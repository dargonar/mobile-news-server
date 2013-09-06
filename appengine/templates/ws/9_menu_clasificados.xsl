{% import 'ws/functions_ex.xsl' as cc %}
<html>
  {{ cc.Head('layout') }}
  <body onload="onLoad('{{page_name}}')" class="{{appid}}">
    <div id="clasificados">
      <div class="columna exsimple">
        <ul class="invisible" id="ul_clasificados">
          {% for item in data.item|build_list %}
          <li><a class="vip2 {{ 'first' if loop.first else ''}}" href="clasificados://{{item.guid.value}}">{{item.title}}</a></li>
          {% endfor %}
        </ul>
      </div>
    </div>
  </body>
</html>