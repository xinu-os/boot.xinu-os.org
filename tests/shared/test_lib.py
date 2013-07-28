from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from shared.views import ProtectedMixin
from accounts.views import AccountsProfileView


class ProtectedMixinTest(TestCase):
    def setUp(self):
        self.username = 'example'
        self.email = 'example@example.org'
        self.password = 'example'
        self.factory = RequestFactory()

    def _login_user(self):
        user = User.objects.create_user(self.username,
                                        self.email,
                                        self.password)
        self.client.login(username=self.username, password=self.password)
        return user

    def test_is_my_account(self):
        user = self._login_user()
        apv = AccountsProfileView()
        apv.kwargs = {'pk': user.pk}
        apv.request = self.factory.get(reverse('accounts:user-profile',
                                               kwargs=apv.kwargs))
        apv.request.user = user
        self.assertTrue(ProtectedMixin.is_my_account(apv))

    def test_is_not_my_account(self):
        user = self._login_user()
        apv = AccountsProfileView()
        apv.kwargs = {'pk': user.pk+1}
        apv.request = self.factory.get(reverse('accounts:user-profile',
                                               kwargs=apv.kwargs))
        apv.request.user = user
        self.assertFalse(ProtectedMixin.is_my_account(apv))
