from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

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

    url(r'^$', TemplateView.as_view(template_name='index.html'),
        name='index'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'),
        name='about'),
)
