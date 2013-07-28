from django.conf.urls import patterns, include, url
from accounts.views import (AccountsProfileView, AccountsRedirectView)

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Add urls here
    url(r'', include('social_auth.urls')),

    url(r'^login/$', 'django.contrib.auth.views.login',
        kwargs={'template_name': 'accounts/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        kwargs={'next_page': '/'}, name='logout'),
    url(r'^(?P<pk>\d+)/$', AccountsProfileView.as_view(), name='user-profile'),
    url(r'^profile/$', AccountsRedirectView.as_view(), name='profile'),
    url(r'^$', AccountsRedirectView.as_view(), name='index'),
)
