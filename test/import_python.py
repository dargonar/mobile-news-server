# ir hasta web/appengine
# correr python2.7 y pastear lo siguiente
import os
import sys
import platform
base_path = os.getcwd()
app_path = base_path
gae_path = os.path.join(base_path, r'C:\Program Files (x86)\Google\google_appengine')

dir1 = '/Applications/GoogleAppEngineLauncher.app/Contents//Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/'
dir2 = os.path.expanduser('~/google-cloud-sdk/platform/google_appengine/')

dirposta = dir1 if os.path.isdir(dir1) else dir2

if platform.system() == 'Darwin': gae_path = os.path.join(base_path, dirposta)

extra_paths=[app_path,os.path.join(app_path, 'lib'),os.path.join(app_path, 'distlib'),gae_path,os.path.join(gae_path, 'lib', 'antlr3'),os.path.join(gae_path, 'lib', 'django'),os.path.join(gae_path, 'lib', 'ipaddr'),os.path.join(gae_path, 'lib', 'webob-1.2.3'),os.path.join(gae_path, 'lib', 'webapp2-2.5.2'),os.path.join(gae_path, 'lib', 'webapp2'),os.path.join(gae_path, 'lib', 'jinja2-2.6'),os.path.join(gae_path, 'lib', 'yaml', 'lib'),os.path.join(gae_path, 'lib', 'lxml-2.3'),]
sys.path = extra_paths + sys.path
from google.appengine.ext import db
from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util
testbed = testbed.Testbed()
testbed.activate()
policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
testbed.init_datastore_v3_stub(consistency_policy=policy)
testbed.init_taskqueue_stub()
testbed.init_urlfetch_stub()
testbed.init_memcache_stub()
print sys.path
