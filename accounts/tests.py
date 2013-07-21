import logging
logging.disable(logging.WARNING)

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from social_auth.tests.client import SocialClient


class AccountsTest(TestCase):
    def setUp(self):
        self.username = 'example'
        self.email = 'example@example.org'
        self.password = 'example'

    def test_local_login(self):
        User.objects.create_user(self.username, self.email, self.password)
        login = self.client.login(username=self.username,
                                  password=self.password)
        self.assertTrue(login)

    def test_social_login(self):
        client = SocialClient()
        user = {'username': self.username,
                'first_name': 'Jane',
                'last_name': 'Doe',
                'email': self.email,
                'id': '53233',
                }
        backends = ('social_auth.backends.facebook.FacebookBackend',)
        backends += settings.AUTHENTICATION_BACKENDS
        with self.settings(AUTHENTICATION_BACKENDS=backends):
            login = client.login(user, backend='facebook')
        # Login was success
        self.assertTrue(login)
        # Make sure associated user was created
        users = User.objects.all()
        self.assertEqual(users.count(), 1)
        # Confirm settings (username, email, and no usable password)
        user = users[0]
        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email, self.email)
        self.assertFalse(user.has_usable_password())
