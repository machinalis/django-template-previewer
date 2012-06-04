from django.conf.urls import patterns, url

urlpatterns = patterns('template_previewer.views',
    url(r'^$', 'preview'),
    url(r'^parse/$', 'parse'),
    url(r'^render/$', 'render'),
)
