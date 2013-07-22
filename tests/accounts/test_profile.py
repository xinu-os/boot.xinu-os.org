import logging
logging.disable(logging.WARNING)

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from social_auth.tests.client import SocialClient
from social_auth.models import UserSocialAuth

from accounts.models import Profile


class AccountsProfileTest(TestCase):
    def setUp(self):
        self.username = 'example'
        self.email = 'example@example.org'
        self.password = 'example'
        self.full_name = 'Jane Doe'

    def _user(self):
        return User.objects.create_user(self.username,
                                        self.email,
                                        self.password)

    def _social_user(self):
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

    def test_get_profile(self):
        user = self._user()
        profile = Profile.objects.get_profile(user)
        self.assertEquals(profile.name, self.username)

    def test_social_get_profile(self):
        user = self._social_user()
        profile = Profile.objects.get_profile(user)
        self.assertEquals(profile.name, self.full_name)
