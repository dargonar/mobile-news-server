{% macro DayMonthYear(item) -%}
  <div class="calendario">{{item.pubDate|datetime('%d')}}</div>
  <div class="calendario">{{item.pubDate|datetime('%m')}}</div>
  <div class="calendario">{{item.pubDate|datetime('%Y')}}</div>
{%- endmacro %}

{% macro avisos_cartelera(items, columna) -%}
  {% for item in items %}
  {% if loop.index0 % 3 == columna %}
  {{ aviso_cartelera(item) }}
  {% endif %}
  {% endfor %}
{%- endmacro %}

{% macro aviso_cartelera(item) -%}
  <div class="rubro">
  {{item.category}}
  </div>
  <div class="cartelera_item">
    <p class="carte_title">{{item.title}}</p>
    <p class="carte_desc">{{item.content.value}}</p>
  </div>
{%- endmacro %}

{% macro avisos_clasificados(items, columna) -%}
  {% for item in items %}
  {% if loop.index0 % 3 == columna and not loop.last %}
  {{ aviso_clasificado(item) }}
  {% endif %}
  {% endfor %}
{%- endmacro %}

{% macro avisos_funebres(items, last_category, columna) -%}
  {% set last_category = '' %}
  {% for item in items %}
  {% if loop.index0 % 3 == columna and not loop.last %}
  {{ aviso_funebre(item, last_category) }}
  {% endif %}
  {% set last_category = item.category %}
  {% endfor %}
{%- endmacro %}

{% macro aviso_funebre(item, last_category) -%}
  {% if last_category != item.category %}
  <div class="rubro">
  {{item.category}}
  </div>
  {% endif %}
  <div class="aviso fune">
    <p>{{item.description}}</p>
  </div>
{%- endmacro %}

{% macro aviso_clasificado(item) -%}
  <div class="aviso clasi">
    <p>{{item.description}}</p>
  </div>
{%- endmacro %}

{% macro avisos_clasificados2(items, columna) -%}
  {% for item in items %}
  {% if loop.index0 % 3 == columna and not loop.last %}
  {{ aviso_clasificado2(item) }}
  {% endif %}
  {% endfor %}
{%- endmacro %}
{% macro aviso_clasificado2(item) -%}
  <div class="aviso clasi">
    <span class="right"><b>{{item.category}}</b></span>
    <span><b>{{item.title}}</b></span>
    <p>{{item.description}}</p>
  </div>
{%- endmacro %}
 
{% macro tablet_open_new_global(node) -%}
<div id="index" class="padded top_padded">
  <div class="nota_abierta">
    {{ DateSectionLabel(node, 'fecha') }}
    <h1>{{node.title}}</h1>
    {% if node.subheader and node.subheader.value and node.subheader.value != 'None' %}
    <p class="subtitulo" id="bajada">{{node.subheader.value}}</p>
    {% endif %}
    <div class="separador">&nbsp;</div>
    
    <div class="fila">
      {% if node.thumbnail %}
        <div class="main_img_container">
          <div class="imagen" id="{{node.thumbnail.attrs.url}}" style="background-image:url({{node.thumbnail.attrs.url}}.i);">
            {{ MediaLink(node, 'video_over_photo')}}
          </div>
        </div>
      {% endif %}
      <div id="informacion" class="contenido">
        {{node|content('html')}}
      </div>
    </div>
  </div>
</div>
{%- endmacro %}

{% macro NoticiaRelacionada(item) -%}
    <li>
      <a href="{{item|related_link}}" title="">
        <div class="titular {{'full_width' if item.attrs.thumbnail == '' else ''}}">
          <div class="header">
            <label class="date">{{item.attrs.pubDate|datetime}}</label>
            {% if item.attrs.category != '' %}
              &nbsp;|&nbsp;
              <label class="seccion">{{ 'Información Gral' if item.attrs.category == 'Información General' else item.attrs.category }}
              </label>
            {% endif %}
          </div>
          <br />
          <label class="titulo">{{item.value}}</label>
        </div>
        
        {% if item.attrs.thumbnail != '' %}
          <div class="foto img_container">
            <div class="imagen_secundaria" id="{{item.attrs.thumbnail}}" style="background-image:url({{item.attrs.thumbnail}}.i) !important;"></div>
            <div class="img_loader">&nbsp;</div>
          </div>
        {% endif %}        
      </a>
      <div class="separador">&nbsp;</div>
    </li>
{%- endmacro %}

{% macro ListadoNoticiasRelacionadas(items) -%}
    <div id="listado" style="display:block;">
      <ul class="main_list">
        {% for item in items %}
        {{ NoticiaRelacionada(item) }}
        {% endfor %}
      </ul>
    </div>
{%- endmacro %}

{% macro TituloSeccionONotisRelac(title) -%}
    <div id="titulo_seccion">
      <label class="lbl_titulo_seccion">{{title}}</label>
    </div>
{%- endmacro %}

{% macro MediaLink(node, container_type) -%}
  {% if node|has_content('any_media') or node.group or node.thumbnail %}
    <div class="media_link {{container_type}}">
    {% if node|has_content('audio') %}
      <a class="ico_audio" href="audio://{{node|content('audio')}}" title="">&nbsp;</a>
    {% endif %}
    {% if node|has_content('audio/mpeg') %}    
      <a class="ico_audio" href="audio://{{node|content('audio/mpeg')}}" title="">&nbsp;</a>
    {% endif %}
    {% if node.group %}
      <a href="galeria://{{node|gallery}}" title="galeria" class="ico_galeria">&nbsp;</a>
    {% endif %}
    {% if not node.group and node.thumbnail %}
      <a href="galeria://{{node.thumbnail.attrs.url}}" title="galeria" class="ico_plus">&nbsp;</a>
    {% endif %}
    {% if node|has_content('video') %}
      <a class="ico_video" href="video://{{node|content('video')}}" title="">&nbsp;</a>
    {% endif %}
    &nbsp;
    </div>
  {% endif %}
{%- endmacro %}

{% macro NotaAbierta(node) -%}
  <div id="nota">
    {% if node.thumbnail %}
      <div class="main_img_container">
      {{ ImagenNoticiaDestacada(node.thumbnail.attrs.url, node.meta) }}
      {{ MediaLink(node, 'video_over_photo') }}
      </div>
    {%else%}
      {{ MediaLink(node, 'no_photo') }}
    {% endif %}
    
    
    <div class="contenido">
      <div id="titulo">
      {{ DateSectionLabel(node) }}
      <br />
      <h1>{{node.title}}</h1>
      </div>
      {% if node.subheader and node.subheader.value and node.subheader.value != 'None' %}
        <div class="bajada" id="bajada">
          {{node.subheader.value}} 
        </div>
      {% endif %}
      <div id="informacion" style="display:block;">
        {{node|content('html')|if_not_none}}
      </div>
    </div>
  </div>
{%- endmacro %}


{% macro tablet_news_list_landscape(nodes, raw_url) -%}
  {% for node in nodes %}
  {{ tablet_news_list_landscape_item(node, raw_url) }}
  {% endfor %}
{%- endmacro %}

{% macro tablet_news_list_landscape_item(node, raw_url) -%}
  <li>  
    <a href="{{node|noticia_link(raw_url)}}" title="principal">
      {% if node.thumbnail %}
      {{ ImagenNoticiaDestacada(node.thumbnail.attrs.url, node.meta, 'imagen') }}
      {% endif %}
      <div class="info"><p>{{node.title}}</p></div>
      {% if not node.thumbnail %}
      <div class="subheader">
        <p>{{node.description|if_not_none}}</p>
      </div>
      {% endif %}
    </a>
  </li>
{%- endmacro %}

{% macro Head(layout) -%}
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <link rel="stylesheet" type="text/css" href="css/{{layout}}.css" />
    <!-- <link rel="stylesheet" type="text/css" href="/mvp_1/stylesheets/{{layout}}.css" /> TEST HACK -->
    <script type="text/javascript" src="js/functions.js"></script>
  </head>
{%- endmacro %}

{% macro UpdatedAt(layout) -%}
  <div id="updated_msg" class="updated hidden">Actualizado hace 1 segundo</div>
{%- endmacro %}

{% macro DateSectionLabel(node, class='date') -%}    
  {% set thedate = node.pubDate|datetime %}
  {% if thedate != '' %}
  <label class="{{class}}">{{thedate}}</label>
  {% endif %}

  {% if node.category and thedate != '' %}
  &nbsp;|&nbsp;
  {% endif %}
  
  {% if node.category %}
  <label class="seccion">
  {% if node.category|trim == 'Información General' %}
    {{ 'Inf. General' }}
  {% else %}
    {% if node.category|trim == 'Nacionales/Internacionales' %}
      {{ 'Nac./Internac.' }}
    {% else %}
      {{ node.category|trim }}
    {% endif %}
  {% endif %}
  </label>
  {% endif %}
  

{%- endmacro %}

{% macro NoticiaEnListado(node) -%}    
    <li>
        <a href="{{node|noticia_link}}" title="">
        <div class="titular {{'' if node.thumbnail else 'full_width'}}">
          <div class="header">
            {{ DateSectionLabel(node) }}
          </div>
          <br />
          <label class="titulo">{{node.title}}</label>
        </div>
        
        {% if node.thumbnail %}
          <div class="foto img_container">
            {% if node.meta %}
              {{ MediaAttach(node.meta) }}
            {% endif %}          
            <div class="imagen_secundaria" id="{{node.thumbnail.attrs.url}}" style="background-image:url({{node.thumbnail.attrs.url}}.i) !important;">&nbsp;</div>
            <div class="img_loader">&nbsp;</div>
          </div>
        {% else %}
            {% if node.meta %}
            <div class="right_ico_container">
              {{ MediaAttach(node.meta) }}
            </div>
            {% endif %}          
        {% endif %}
        </a>
        <div class="separador">&nbsp;</div>
    </li>
{%- endmacro %}

{% macro MediaAttach(meta) -%}
    <div class="ico_container">
      {% if meta|meta_has('gallery') %}
      <div class="ico_galeria">&nbsp;</div>
      {% endif %}
      {% if meta|meta_has('video') %}
      <div class="ico_video">&nbsp;</div>
      {% endif %}
      {% if meta|meta_has('audio') %}
      <div class="ico_audio">&nbsp;</div>
      {% endif %}
    &nbsp;
    </div>    
{%- endmacro %}

{% macro ImagenNoticiaDestacada(url, meta, class='imagen_principal') -%}
    <div class="{{class}}" id="{{url}}" style="background-image:url({{url}}.i);">
      <div class="media_link video_over_photo">
        {{ MediaAttach(meta) }}
      </div>
    </div>
{%- endmacro %}

{% macro DestacadaEnListadoPrincipal(node) -%}
    <div id="nota">
      <a href="{{node|noticia_link}}" title="principal">
        {% if node.thumbnail %}
          {{ ImagenNoticiaDestacada(node.thumbnail.attrs.url, node.meta) }}
        {% endif %}
        <div class="contenido">
          <div id="titulo">
            {% if node.pubDate %}
            <label>{{node.pubDate|datetime}}</label> | <label class="seccion">{{node.category}}</label>
            <br />
            {% endif %}
            <h1>{{node.title}}</h1>
          </div>
        </div>
      </a>
      <div class="separador">&nbsp;</div>
    </div>    
{%- endmacro %}

{% macro ListadoNoticiasEnListado(nodes) -%}

  <div id="listado" style="display:block;">
    <ul class="main_list">
      {% for node in nodes %}
        {{ NoticiaEnListado(node) }}
      {% endfor %}
    </ul>
  </div>
    
{%- endmacro %}

{% macro tablet_index_portrait_main(node, raw_url) -%}
    <a href="{{node|noticia_link(raw_url)}}" title="principal">
      <div class="nota_principal">
        <div class="info">
          <div class="encabezado">
              {{ DateSectionLabel(node) }}
              <h1>{{node.title}}</h1>
              <p class="subtitulo">{{node.description|if_not_none}}</p>
          </div>
        </div>
        {% if node.thumbnail %}
          {{ ImagenNoticiaDestacada(node.thumbnail.attrs.url, node.meta, 'imagen') }}
        {% endif %}
      </div>
    </a>
    <div class="separador">&nbsp;</div>
{%- endmacro %}

{% macro tablet_index_portrait_secondary(nodes, raw_url) -%}
    {% for node in nodes %}
      {{ tablet_index_portrait_secondary_item(node, 'last' if loop.last else '', raw_url) }}
    {% endfor %}
    <div class="separador">&nbsp;</div>
{%- endmacro %}

{% macro tablet_index_portrait_secondary_item(node, class, raw_url) -%}
    <a href="{{node|noticia_link(raw_url)}}" title="principal">
      <div class="nota_secundaria {{class}}">
        {{ DateSectionLabel(node) }}
        <h1>{{node.title}}</h1>
        {% if node.thumbnail %}
          {{ ImagenNoticiaDestacada(node.thumbnail.attrs.url, node.meta, 'imagen') }}
        {% else %}
        <div class="info">
          <p>{{node.description|if_not_none}}</p>
        </div>
        {% endif %}
      </div>
    </a>
{%- endmacro %}

{% macro tablet_index_portrait_terciary(nodes, raw_url) -%}
    {% for node in nodes %}
      {{ tablet_index_portrait_terciary_item(node, 'last' if loop.index % 3 == 0 else '', raw_url) }}
      {% if loop.index % 3 == 0 %}
      <div class="separador">&nbsp;</div>
      {% endif %}
    {% endfor %}
{%- endmacro %}

{% macro tablet_index_portrait_terciary_item(node, class, raw_url) -%}
    <a href="{{node|noticia_link(raw_url)}}" title="principal">
      <div class="nota_terciaria {{class}}">
        {{ DateSectionLabel(node) }}
        <h2>{{node.title}}</h2>
        {% if node.thumbnail %}
          {{ ImagenNoticiaDestacada(node.thumbnail.attrs.url, node.meta, 'imagen') }}
        {% else %}
        <div class="info">
          <p>{{node.description|if_not_none}}</p>
        </div>
        {% endif %}
      </div>
    </a>
{%- endmacro %}
