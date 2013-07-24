import logging
logging.disable(logging.WARNING)

import httplib

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from kernels.models import Kernel


class KernelsUploadTest(TestCase):
    def setUp(self):
        self.url = reverse('kernels:upload')
        self.password1 = 'password1'
        self.user1 = User.objects.create_user('user1',
                                              'user1@example.org',
                                              self.password1)
        self.user1.plaintext = self.password1
        self.password2 = 'password2'
        self.user2 = User.objects.create_user('user2',
                                              'user2@example.org',
                                              self.password2)
        self.user2.plaintext = self.password2

    def _login_user(self, user):
        login = self.client.login(username=user.username,
                                  password=user.plaintext)
        return login

    def _submit_upload(self, user):
        with open(settings.TEST_DATA_PATH.child('example.bin')) as f:
            # Read file for testing later
            contents = f.read()
            # Reset to beginning
            f.seek(0)
            response = self.client.post(self.url, {
                'owner': user.pk,
                'image': f,
                'access_level': Kernel.ACCESS_LEVELS[0][0],
            })
        return response, contents

    def test_upload(self):
        self.assertTrue(self._login_user(self.user1))
        response, contents = self._submit_upload(self.user1)
        kernels = Kernel.objects.all()
        self.assertEqual(kernels.count(), 1)
        kernel = kernels[0]
        self.assertEqual(contents, kernel.image.read())
        self.assertRedirects(response, reverse('kernels:view',
                                               kwargs={'pk': kernel.pk}))

    def test_upload_no_login(self):
        response, contents = self._submit_upload(self.user1)
        kernels = Kernel.objects.all()
        self.assertEqual(kernels.count(), 0)
        login_url = reverse('accounts:login')
        next_url = self.url
        url = '{0}?next={1}'.format(login_url, next_url)
        self.assertRedirects(response, url)

    def test_upload_other_user(self):
        # Login as user1
        self.assertTrue(self._login_user(self.user1))
        # Claim that the upload came from user2
        response, contents = self._submit_upload(self.user2)
        kernels = Kernel.objects.all()
        self.assertEqual(kernels.count(), 0)
        # user doesn't match owner, forbidden
        self.assertEqual(response.status_code, httplib.FORBIDDEN)
