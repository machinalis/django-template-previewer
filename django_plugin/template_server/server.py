import sys
import socket
import os.path
from django.conf import settings
from django.utils.importlib import import_module

# Add the plugin path to sys.path
cwd = os.path.abspath(__file__)
plugin_base = os.path.join(os.path.dirname(cwd), os.pardir)
sys.path.append(os.path.normpath(plugin_base))

def parse_command_line(argv=None):
    """
    Returns a tupple with the project path and settings module name
    Default settings module name is "settings"
    """
    if argv is None:
        argv = sys.argv
    if len(argv) not in (2, 3):
        sys.stderr.write("Usage: server.py project_path [settings_module]\n\n")
        sys.exit(1)

    path = sys.argv[1]
    if path[-1] == '/': path=path[:-1]

    if len(sys.argv) == 3:
        settings_module_name = sys.argv[2]
    else:
        settings_module_name = 'settings'
    return path, settings_module_name

def django_setup(settings_module_name):
    """
    Configure django to not need DJANGO_SETTINGS_MODULE

    Some settings are pulled from the module named settings_module_name, if
    they affect template rendering. Most settings are left with a default. A
    few are hardcoded to minimal values.
    """
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
    minimal_settings['DATABASES'] = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'mydatabase'
        }
    }
    settings.configure(**minimal_settings)

def find_open_port():
    """Finds an available TCP port number"""
    s = socket.socket()
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port

def run_server(port):
    """run a base-configured django server on 127.0.0.1:port"""
    from django.core.management import execute_from_command_line
    execute_from_command_line([__name__, 'runserver', '--noreload', str(port)])

def main():
    project_path, settings_module = parse_command_line(sys.argv)

    # These two paths are usually in the sys.path for django projects
    sys.path.append(os.path.join(project_path, '..'))
    sys.path.append(project_path)

    django_setup(settings_module)
    port = find_open_port()
    run_server(port)

if __name__ == "__main__":
    main()
