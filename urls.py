from django.conf.urls.defaults import url, patterns

from slurpee.views import slurp

urlpatterns = patterns('',
  url(r'^$', slurp, name='slurper'),
)
