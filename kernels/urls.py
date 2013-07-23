from django.conf.urls import patterns, url
from kernels.views import KernelsUploadView, KernelsImageView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Add urls here
    url(r'^upload/$', KernelsUploadView.as_view(), name='upload'),
    url(r'^view/(?P<pk>[0-9a-fA-F]{40})/$', KernelsImageView.as_view(),
        name='view'),
)
