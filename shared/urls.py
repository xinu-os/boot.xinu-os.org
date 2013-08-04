from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from shared.views import S3SignerView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Add urls here
    url(r'^sign_s3/$', S3SignerView.as_view(), name='s3-signer'),
)
