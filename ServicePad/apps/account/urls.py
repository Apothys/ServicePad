from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

urlpatterns = patterns('ServicePad.apps.account.views',
    (r'^$', 'index'),
    (r'^teams/$','teams'),
    (r'^profile/$','profile'),
    (r'^events/$','events'),
    (r'^logout/$','logout')
)
