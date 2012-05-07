import sys
import socket
import os.path
from django.conf import settings
from django.utils.importlib import import_module

cwd = os.path.abspath(__file__)
plugin_base = os.path.join(os.path.dirname(cwd), os.pardir)
sys.path.append(os.path.normpath(plugin_base))

# Parse command line

path = sys.argv[1]
if path[-1] == '/': path=path[:-1]

if len(sys.argv) >= 3:
    settings_module_name = sys.argv[2]
else:
    settings_module_name = 'settings'

# Django adds the project path
sys.path.append(os.path.dirname(path))

# Configure django with ONLY the settings relevant to serve templates
sys.path.append(path)
project_module = import_module(settings_module_name)
minimal_settings = {}
PRESENTATION_RELATED_SETTINGS = [
    'ALLOWED_INCLUDE_ROOTS',  # used by {% ssi tag %}
    'DATE_FORMAT',
    'DATETIME_FORMAT',
    'DECIMAL_SEPARATOR',
    'FIRST_DAY_OF_WEEK',
    'INSTALLED_APPS',
    'LANGUAGE_CODE',
    'LANGUAGES',
    'LOCALE_PATHS',
    'MONTH_DAY_FORMAT',
    'NUMBER_GROUPING',
    'RESTRUCTUREDTEXT_FILTER_SETTINGS',
    'ROOT_URLCONF',
    'SHORT_DATE_FORMAT',
    'SHORT_DATETIME_FORMAT',
    'STATIC_URL',
    'TEMPLATE_DIRS',
    'TEMPLATE_LOADERS',
    'TEMPLATE_STRING_IF_INVALID',
    'THOUSAND_SEPARATOR',
    'TIME_FORMAT',
    'USE_I18N',
    'USE_L10N',
    'USE_THOUSAND_SEPARATOR',
    'YEAR_MONTH_FORMAT',
]
for s in PRESENTATION_RELATED_SETTINGS:
    if hasattr(project_module, s):
        minimal_settings[s] = getattr(project_module, s)
# Force some default values
minimal_settings['MIDDLEWARE_CLASSES'] = (
    'django.middleware.common.CommonMiddleware',
    'template_preview_middleware.TemplatePreviewMiddleware',
)
minimal_settings['TEMPLATE_CONTEXT_PROCESSORS'] = (
    "django.core.context_processors.i18n",
    "django.core.context_processors.static"
)
minimal_settings['DEBUG'] = True
minimal_settings['TEMPLATE_DEBUG'] = True
minimal_settings['SOUTH_DATABASE_ADAPTERS'] = {'default': 'south.db.sqlite3'}

settings.configure(**minimal_settings)

# Find an open socket number
s = socket.socket()
s.listen(1)
port = s.getsockname()[1]
s.close()

# run a simple server
from django.core.management import execute_from_command_line
execute_from_command_line([__name__, 'runserver', '--noreload', str(port)])

