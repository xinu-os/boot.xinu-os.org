from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from kernels.views import (KernelsUploadView, KernelsView,
                           KernelsDeleteView)

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Add urls here
    url(r'^upload/$', KernelsUploadView.as_view(), name='upload'),
    url(r'^(?P<pk>[0-9a-fA-F]{40})/$', KernelsView.as_view(),
        name='view'),
    url(r'^(?P<pk>[0-9a-fA-F]{40})/delete/$', KernelsDeleteView.as_view(),
        name='delete'),
    url(r'^$', TemplateView.as_view(template_name='kernels/index.html'),
        name='index'),
)
