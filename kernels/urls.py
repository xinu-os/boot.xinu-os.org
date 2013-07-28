from django.conf.urls import patterns, url
from kernels.views import (KernelsUploadView, KernelsImageView,
                           KernelsView, KernelsDeleteView)

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
    url(r'^(?P<pk>[0-9a-fA-F]{40})/image.bin$', KernelsImageView.as_view(),
        name='image'),
)
