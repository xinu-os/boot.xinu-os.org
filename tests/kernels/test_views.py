import logging
logging.disable(logging.WARNING)

import httplib
import tempfile
import shutil

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from kernels.models import Kernel


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
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

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def _login_user(self, user):
        login = self.client.login(username=user.username,
                                  password=user.plaintext)
        return login

    def _submit_upload(self, user):
        content = 'DATA'
        f = ContentFile(content, 'content_file')
        response = self.client.post(self.url, {
            'owner': user.pk,
            'image': f,
            'access_level': Kernel.ACCESS_LEVELS[0][0],
        })
        return response, content

    def test_upload(self):
        self.assertTrue(self._login_user(self.user1))
        response, contents = self._submit_upload(self.user1)
        self.kernels = Kernel.objects.all()
        self.assertEqual(self.kernels.count(), 1)
        kernel = self.kernels[0]
        self.assertEqual(contents, kernel.image.read())
        self.assertRedirects(response, reverse('kernels:view',
                                               kwargs={'pk': kernel.pk}))

    def test_upload_no_login(self):
        response, contents = self._submit_upload(self.user1)
        self.kernels = Kernel.objects.all()
        self.assertEqual(self.kernels.count(), 0)
        login_url = reverse('accounts:login')
        next_url = self.url
        url = '{0}?next={1}'.format(login_url, next_url)
        self.assertRedirects(response, url)

    def test_upload_other_user(self):
        # Login as user1
        self.assertTrue(self._login_user(self.user1))
        # Claim that the upload came from user2
        response, contents = self._submit_upload(self.user2)
        self.kernels = Kernel.objects.all()
        self.assertEqual(self.kernels.count(), 0)
        # user doesn't match owner, forbidden
        self.assertEqual(response.status_code, httplib.FORBIDDEN)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class KernelsDetailViewTest(TestCase):

    def setUp(self):
        # two users, user 1 has 3 images
        self.pass1 = 'z'
        self.user1 = User.objects.create_user('a', 'a@example.com', self.pass1)
        self.user2 = User.objects.create_user('b', 'b@example.com', 'y')
        # images
        self.kernel0 = self._create_kernel(Kernel.ACCESS_PUBLIC)
        self.kernel1 = self._create_kernel(Kernel.ACCESS_LINK)
        self.kernel2 = self._create_kernel(Kernel.ACCESS_PRIVATE)

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def _create_kernel(self, access_level):
        f = ContentFile(Kernel.ACCESS_LEVELS[access_level][1], 'content_file')
        kernel = Kernel.objects.create(owner=self.user1, image=f,
                                       access_level=access_level)
        return kernel

    def _get_detail_url(self, pk):
        return reverse('kernels:view', kwargs={'pk': pk})

    def _get_image_url(self, pk):
        return reverse('kernels:image', kwargs={'pk': pk})

    def _assertViewable(self, kernel):
        # KernelsDetailView
        url = self._get_detail_url(kernel.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kernels/view.html')
        # KernelsImageView
        url = self._get_image_url(kernel.pk)
        response = self.client.get(url, HTTP_REFERER=url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, kernel.image.read())

    def _assertNonViewable(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_public_view(self):
        # A public kernel can be viewed globally
        self._assertViewable(self.kernel0)

    def test_link_only_view(self):
        # A link-only kernel can be viewed globally
        self._assertViewable(self.kernel1)

    def test_private_view_owner(self):
        # A private kernel can only be viewed by owner
        login = self.client.login(username=self.user1.username,
                                  password=self.pass1)
        self.assertTrue(login)
        self._assertViewable(self.kernel2)

    def test_private_view_non_owner(self):
        self._assertNonViewable(self._get_detail_url(self.kernel2.pk))
        self._assertNonViewable(self._get_image_url(self.kernel2.pk))
