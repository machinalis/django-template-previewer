Django Template Previewer
=========================

This is a django app to be used in development environments only. Its
purpose is to allow template writers to preview rendering of the templates
providing a handcrafted context, without having to write view code.

Its goal it's provide template designers a way to test designs and UI without
having to modify code, or generate custom data.

Installation
============

You can install as any standard python package, from zip file or pypi:

    pip install django-template-previewer

After that, all you need to do is enable the app into your django project
adding it to the `INSTALLED_APPS` setting in `settings.py`:

```python
INSTALLED_APPS = (
    # ... yor regular apps here

    'template_previewer',
)
```

Also, you should include url routes from the app into your `urls.py`:

```python
    urlpatterns = patterns('',
        url(r'^_preview/', include('template_previewer.urls')),
        # ..Your regular URL patterns here
    )
```

**You should disable the application in production environments, as it exposes
implementations details, and may allow unauthorized access to data and execution
of code.**

No syncdb/migration is required; this application does not use the database.

The app assumes you are using Django's app template loader and app staticfile
finder. Otherwise, its views won't work properly.

Note that you require Django 1.4

Usage
=====

Assuming you installed using the url route in the example above, and that you
are using the standard django development server locally 
(`manage.py runserver`), you should get the template previewer UI by visiting
<http://localhost:8000/_preview/> with your browser. Javascript is required.

You should see something similar to:

![Screenshot](https://raw.github.com/machinalis/django-template-previewer/master/doc/ss-initial.png)

The lower box is an html `iframe` where the preview will be shown. The template
previewer UI can be folded/unfolded by clicking on its title.

There you can type a template name in the text box, and click on 
"Update context". The template name should be written as a path reachable to
your template loader (i.e., any valid first argument to
`django.template.loader.get_template`). If the template is reachable and can
be successfully loaded, the previewer UI will add entry boxes labeled with the
names of template variables required in the template.

For example, assuming we have the following template calles `sample.html`:

```html
<h1>{{ title }}</h1>
<ul>
{% for item in foo.bar %}
    <li>{{ item.last_name }}, {{ item.first_name }}</li>
{% endfor %}
<ul>
```

You'll get something like:

![Screenshot](https://raw.github.com/machinalis/django-template-previewer/master/doc/ss-with-context.png)

There you can fill up some values, and click on Preview, getting the following:

![Screenshot](https://raw.github.com/machinalis/django-template-previewer/master/doc/ss-with-preview.png)

or, hiding the previewer UI:

![Screenshot](https://raw.github.com/machinalis/django-template-previewer/master/doc/ss-full-preview.png)

That's essentially all there is to it. You can keep editing the context and 
refreshing the preview. If you are using the development server, updating the
template file and clicking preview again should refresh too (allowing for a 
quick edit+preview cycle once you have a nice sample context ready)

Licensing
=========

This package was written by Daniel F. Moisset <dmoisset@machinalis.com> at
Machinalis, and is © Machinalis, licensed under the BSD (see LICENSE for
details).

Javascript files included in the `template_previewer/static/js` directory (but
not its subdirectories) are third party libraries, copyright their respective
owners. Check the files for licensing details.

