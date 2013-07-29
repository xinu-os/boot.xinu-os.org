import logging
logging.disable(logging.WARNING)

from django.test import TestCase
from django.test.client import RequestFactory
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from social_auth.tests.client import SocialClient
from social_auth.models import UserSocialAuth

from accounts.views import AccountsProfileView


class AccountsRedirectView(TestCase):
    def setUp(self):
        self.username = 'example'
        self.email = 'example@example.org'
        self.password = 'example'
        self.user = User.objects.create_user(self.username,
                                             self.email,
                                             self.password)

    def test_no_user(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertRedirects(response, reverse('accounts:login'))

    def test_with_user(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('accounts:profile'))
        self.assertRedirects(response, reverse('accounts:user-profile',
                                               kwargs={'pk': self.user.pk}))


class AccountsProfileTest(TestCase):
    def setUp(self):
        self.username = 'example'
        self.email = 'example@example.org'
        self.password = 'example'
        self.full_name = 'Jane Doe'
        self.factory = RequestFactory()

    def _login_user(self):
        user = User.objects.create_user(self.username,
                                        self.email,
                                        self.password)
        self.client.login(username=self.username, password=self.password)
        return user

    def _login_social_user(self):
        client = SocialClient()
        user = {'username': self.username,
                'first_name': self.full_name.split()[0],
                'last_name': self.full_name.split()[1],
                'email': self.email,
                'id': '53233',
                }
        backends = ('social_auth.backends.facebook.FacebookBackend',)
        backends += settings.AUTHENTICATION_BACKENDS
        with self.settings(AUTHENTICATION_BACKENDS=backends):
            client.login(user, backend='facebook')
        # Make sure associated user was created
        social_user = UserSocialAuth.objects.all()[0]
        return social_user.user

    def test_get_form_with_post(self):
        web_site = 'http://localhost/'
        user = self._login_social_user()
        apv = AccountsProfileView()
        apv.kwargs = {'pk': user.pk}
        apv.request = self.factory.post(reverse('accounts:user-profile',
                                                kwargs=apv.kwargs))
        apv.request.POST = {'web_site': web_site}
        apv.request.user = user
        form = apv.get_form(apv.form_class)
        self.assertEqual(form.data['web_site'], web_site)
        self.assertEqual(form.instance.name, self.full_name)

    def test_get_form_without_post(self):
        user = self._login_social_user()
        apv = AccountsProfileView()
        apv.kwargs = {'pk': user.pk}
        apv.request = self.factory.get(reverse('accounts:user-profile',
                                       kwargs=apv.kwargs))
        apv.request.user = user
        form = apv.get_form(apv.form_class)
        self.assertEqual(form.instance.name, self.full_name)

    def test_profile_get_without_user(self):
        user = self._login_user()
        self.client.logout()
        response = self.client.get(reverse('accounts:user-profile',
                                           kwargs={'pk': user.pk}))
        # Form is in context, but cannot be post'd to
        self.assertIn('form', response.context_data)

    def test_profile_get_with_user(self):
        user = self._login_user()
        response = self.client.get(reverse('accounts:user-profile',
                                           kwargs={'pk': user.pk}))
        self.assertIn('form', response.context_data)

    def test_profile_post_without_user(self):
        user = self._login_user()
        self.client.logout()
        response = self.client.post(reverse('accounts:user-profile',
                                            kwargs={'pk': user.pk}),
                                    {'name': 'My Name'})
        self.assertRedirects(response, reverse('accounts:profile'),
                             target_status_code=302)

    def test_profile_post_with_user(self):
        user = self._login_user()
        name = 'My Name'
        target_url = reverse('accounts:user-profile', kwargs={'pk': user.pk})
        response = self.client.post(target_url, {
            'name': name,
            'email': user.email
        })
        self.assertRedirects(response, target_url)
        # confirm that name was saved
        response = self.client.get(target_url)
        self.assertIn('form', response.context_data)
        self.assertEqual(response.context_data['form'].instance.name, name)

    def test_profile_post_with_baddata(self):
        user = self._login_user()
        bad_site = 'INVALID'
        target_url = reverse('accounts:user-profile', kwargs={'pk': user.pk})
        response = self.client.post(target_url, {'web_site': bad_site})
        errors = ['Enter a valid URL.']
        self.assertFormError(response, 'form', 'web_site', errors)

