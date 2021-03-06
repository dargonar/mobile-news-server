# -*- coding: utf-8 -*-
"""
    tipfyext.jinja2.scripts
    ~~~~~~~~~~~~~~~~~~~~~~~

    Command line utilities for Jinja2.

    :copyright: 2011 by tipfy.org.
    :license: BSD, see LICENSE.txt for more details.
"""
import os
import sys
import platform

base_path = os.getcwd()
app_path = os.path.join(base_path, 'appengine')

if platform.system() == 'Darwin':

  dir1 = '/Applications/GoogleAppEngineLauncher.app/Contents//Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/'
  dir2 = os.path.expanduser('~/google-cloud-sdk/platform/google_appengine/')
  dirposta = dir1 if os.path.isdir(dir1) else dir2

  gae_path = os.path.join(base_path, dirposta)
else:
  gae_path = os.path.join(base_path, r'C:\Program Files (x86)\Google\google_appengine')

extra_paths = [
    app_path,
    os.path.join(app_path, 'lib'),
    os.path.join(app_path, 'distlib'),
    gae_path,
    # These paths are required by the SDK.
    os.path.join(gae_path, 'lib', 'antlr3'),
    os.path.join(gae_path, 'lib', 'django'),
    os.path.join(gae_path, 'lib', 'ipaddr'),
    os.path.join(gae_path, 'lib', 'webob-1.2.3'),
    os.path.join(gae_path, 'lib', 'webapp2-2.5.2'),
    os.path.join(gae_path, 'lib', 'webapp2'),
    os.path.join(gae_path, 'lib', 'jinja2-2.6'),
    os.path.join(gae_path, 'lib', 'yaml', 'lib'),
    os.path.join(gae_path, 'lib', 'lxml-2.3'),
]

sys.path = extra_paths + sys.path

print sys.path

from jinja2 import FileSystemLoader
from webapp2_extras import jinja2
import webapp2

def walk(top, topdown=True, onerror=None, followlinks=False):
    """Borrowed from Python 2.6.5 codebase. It is os.walk() with symlinks."""
    try:
        names = os.listdir(top)
    except os.error, err:
        if onerror is not None:
            onerror(err)
        return

    dirs, nondirs = [], []
    for name in names:
        if os.path.isdir(os.path.join(top, name)):
            dirs.append(name)
        else:
            nondirs.append(name)

    if topdown:
        yield top, dirs, nondirs
    for name in dirs:
        path = os.path.join(top, name)
        if followlinks or not os.path.islink(path):
            for x in walk(path, topdown, onerror, followlinks):
                yield x
    if not topdown:
        yield top, dirs, nondirs


def list_templates(self):
    """Monkeypatch for FileSystemLoader to follow symlinks when searching for
    templates.
    """
    print 'lt: %s' % self.searchpath
    
    found = set()
    for searchpath in self.searchpath:
        for dirpath, dirnames, filenames in walk(searchpath, followlinks=True):
            for filename in filenames:
                template = os.path.join(dirpath, filename) \
                    [len(searchpath):].strip(os.path.sep) \
                                      .replace(os.path.sep, '/')
                if template[:2] == './':
                    template = template[2:]
                if template not in found:
                    found.add(template)
    return sorted(found)


def logger(msg):
    sys.stderr.write('%s\n' % msg)


def filter_templates(tpl):
    # ignore templates that start with '.' and py files.
    if os.path.basename(tpl).startswith('.'):
        return False

    if os.path.basename(tpl).endswith(('.py', '.pyc', '.zip')):
        return False

    return True


def compile_templates(argv=None):
    """Compiles templates for better performance. This is a command line
    script. From the buildout directory, run:

        bin/jinja2_compile

    It will compile templates from the directory configured for 'templates_dir'
    to the one configured for 'templates_compiled_target'.

    At this time it doesn't accept any arguments.
    """
    if argv is None:
        argv = sys.argv

    from config import config

    app = webapp2.WSGIApplication(config=config)

    template_path = 'templates'
    compiled_path = 'templates_compiled'

    if compiled_path is None:
        raise ValueError('Missing configuration key to compile templates.')

    if isinstance(template_path, basestring):
        # A single path.
        source = os.path.join(app_path, template_path)
    else:
        # A list of paths.
        source = [os.path.join(app_path, p) for p in template_path]

    #print app_path, '->', template_path, '->', compiled_path
    target = os.path.join(app_path, compiled_path)
    
    print 'source: %s' % source
    print 'target: %s' % target
    
    # Set templates dir and deactivate compiled dir to use normal loader to
    # find the templates to be compiled.
        # 'template_path': 'templates',\
        # 'compiled_path': None,

    config['webapp2_extras.jinja2']['template_path'] = source
    config['webapp2_extras.jinja2']['compiled_path'] = None

    if target.endswith('.zip'):
        zip_cfg = 'deflated'
    else:
        zip_cfg = None

    old_list_templates = FileSystemLoader.list_templates
    FileSystemLoader.list_templates = list_templates

    env = jinja2.get_jinja2(app=app).environment
    # from myfilters import do_currencyfy, do_statusfy, do_pricefy, do_addressify, do_descriptify, do_headlinify, do_slugify, do_operationfy, do_totalareafy, do_expensasfy, do_add_days, do_realestate_linkfy, do_ownerify, do_oper_labelify, do_email_to_png

    from utils import url_fix,format_datetime,noticia_link,if_not_none,has_content,get_content,gallery,meta_has,related_link,build_list,empty
    env.filters['urlencode']    = url_fix
    env.filters['datetime']     = format_datetime
    env.filters['noticia_link'] = noticia_link
    env.filters['if_not_none']  = if_not_none
    env.filters['has_content']  = has_content
    env.filters['content']      = get_content
    env.filters['gallery']      = gallery
    env.filters['meta_has']     = meta_has
    env.filters['related_link'] = related_link
    env.filters['build_list']   = build_list
    env.filters['is_empty']     = empty
    env.compile_templates(target, extensions=None,
        filter_func=filter_templates, zip=zip_cfg, log_function=logger,
        ignore_errors=False, py_compile=False)

    FileSystemLoader.list_templates = old_list_templates


compile_templates()
