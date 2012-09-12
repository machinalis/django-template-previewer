from distutils.core import setup

with open('README.md') as readme:
    __doc__ = readme.read()

setup(
    name='django-template-previewer',
    version='0.1.3',
    description=u'A Django app to allow developers preview templates',
    long_description=__doc__,
    author=u'Daniel F. Moisset',
    author_email='dmoisset@machinalis.com',
    url='https://github.com/machinalis/django-template-previewer',
    packages=['template_previewer', 'template_previewer.template_parser'],
    include_package_data=True,
    package_data = {
        "template_previewer": [
            "templates/template_previewer/*.html",
            "static/css/template_previewer/*.css",
            "static/js/template_previewer/*.js",
            "static/js/*.js",
        ]
    },    zip_safe=False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
