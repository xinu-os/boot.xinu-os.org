from mock import patch

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase

from kernels.models import Kernel
from shared.views import S3SignerView


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

    def _login_user(self, user):
        return self.client.login(username=user.username,
                                 password=user.plaintext)

    def _submit_upload(self, user):
        access_level = Kernel.ACCESS_PUBLIC
        self.assertTrue(self._login_user(user))
        signer = S3SignerView()
        image_hash = signer.get_hash(user)
        image_path = 'https://example.org/{0}/{1}.bin'
        image_path = image_path.format(image_hash[0:2], image_hash)
        response = self.client.post(self.url, {
            'owner': user.pk,
            'image_path': image_path,
            'access_level': access_level,
        })
        self.client.logout()
        return response

    @patch('shared.views.settings')
    def test_upload_same_image_two_users(self, mock_conf):
        mock_conf.AWS_SECRET_ACCESS_KEY = 'A'*20
        # Upload kernel once
        self._submit_upload(self.user1)
        self.kernels = Kernel.objects.all()
        self.assertEqual(self.kernels.count(), 1)
        # Upload same kernel as different user
        self._submit_upload(self.user2)
        self.kernels = Kernel.objects.all()
        self.assertEqual(self.kernels.count(), 2)
