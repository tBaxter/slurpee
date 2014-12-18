from django.conf.urls.defaults import url, patterns

from .views import slurp

urlpatterns = patterns('',
  url(r'^$', slurp, name='slurper'),
)
