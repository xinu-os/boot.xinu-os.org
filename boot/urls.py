from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'boot.views.home', name='home'),
    # url(r'^boot/', include('boot.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tracking/', include('tracking.urls', namespace='tracking')),

    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^kernels/', include('kernels.urls', namespace='kernels')),
)
