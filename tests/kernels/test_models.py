import tempfile
import shutil

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings

from kernels.models import Kernel


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class KernelsModelTestCase(TestCase):

    def setUp(self):
        self.url = reverse('kernels:upload')
        self.user1 = User.objects.create_user('user1',
                                              'user1@example.org',
                                              'password1')
        self.user1.plaintext = 'password1'
        self.user2 = User.objects.create_user('user2',
                                              'user2@example.org',
                                              'password2')
        self.user2.plaintext = 'password2'

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def _login_user(self, user):
        return self.client.login(username=user.username,
                                 password=user.plaintext)

    def _submit_upload(self, user, access_level=None):
        if access_level is None:
            access_level = Kernel.ACCESS_PUBLIC
        self.assertTrue(self._login_user(user))
        content = 'DATA'
        f = ContentFile(content, 'content_file')
        response = self.client.post(self.url, {
            'owner': user.pk,
            'image': f,
            'access_level': access_level,
        })
        self.client.logout()
        return response, content

    def test_upload_same_image_twice(self):
        # Upload kernel once
        response, content = self._submit_upload(self.user1)
        self.kernels = Kernel.objects.all()
        self.assertEqual(self.kernels.count(), 1)
        kernel = self.kernels[0]
        self.assertEqual(content, kernel.image.read())
        # Upload same kernel as same user, but change access_level
        access_level = Kernel.ACCESS_LINK
        response, content = self._submit_upload(self.user1, access_level)
        self.kernels = Kernel.objects.all()
        self.assertEqual(self.kernels.count(), 1)
        kernel = self.kernels[0]
        self.assertEqual(content, kernel.image.read())
        self.assertEqual(access_level, kernel.access_level)

    def test_upload_same_image_two_users(self):
        # Upload kernel once
        response, contents = self._submit_upload(self.user1)
        self.kernels = Kernel.objects.all()
        self.assertEqual(self.kernels.count(), 1)
        kernel = self.kernels[0]
        self.assertEqual(contents, kernel.image.read())
        # Upload same kernel as different user
        response, contents = self._submit_upload(self.user2)
        self.kernels = Kernel.objects.all()
        self.assertEqual(self.kernels.count(), 2)
        kernel = self.kernels[1]
        self.assertEqual(contents, kernel.image.read())
        self.assertNotEqual(*self.kernels)
