from django.test import TestCase
from django.contrib.auth.models import User
from social_auth.tests.client import SocialClient


class AccountsTest(TestCase):
    def test_local_login(self):
        username = 'example'
        email = 'example@example.org'
        password = 'example'
        user = User.objects.create_user(username, email, password)
        login = self.client.login(username=username, password=password)
        self.assertTrue(login)

    def test_social_login(self):
        client = SocialClient
        user = {}
        login = client.login(user, backend='facebook')
        self.assertTrue(login)
