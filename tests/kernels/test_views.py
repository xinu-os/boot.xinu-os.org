import logging
logging.disable(logging.WARNING)

import httplib

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson as json

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

    def _submit_upload(self, user, **kwargs):
        hash_ = '93c795e321598d6d61403cb62ab30b8a1660bbc8'
        path = '{0}/{1}.bin'.format(hash_[0:2], hash_)
        response = self.client.post(self.url, {
            'owner': user.pk,
            'image_path': 'https://example.org/{0}'.format(path),
            'access_level': Kernel.ACCESS_LEVELS[0][0],
        }, **kwargs)
        return response

    def test_upload(self):
        self.assertTrue(self._login_user(self.user1))
        response = self._submit_upload(self.user1)
        self.kernels = Kernel.objects.all()
        self.assertEqual(self.kernels.count(), 1)
        kernel = self.kernels[0]
        self.assertRedirects(response, reverse('kernels:view',
                                               kwargs={'pk': kernel.pk}))

    def test_upload_ajax(self):
        self.assertTrue(self._login_user(self.user1))
        response = self._submit_upload(
            self.user1,
            follow=True,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.kernels = Kernel.objects.all()
        self.assertEqual(self.kernels.count(), 1)
        kernel = self.kernels[0]
        url = reverse('kernels:view', kwargs={'pk': kernel.pk})
        self.assertRedirects(response, url)
        response = json.loads(response.content)
        redirect = response['redirect']
        self.assertEqual(redirect, url)

    def test_upload_no_login(self):
        response = self._submit_upload(self.user1)
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
        response = self._submit_upload(self.user2)
        self.kernels = Kernel.objects.all()
        self.assertEqual(self.kernels.count(), 0)
        # user doesn't match owner, forbidden
        self.assertEqual(response.status_code, httplib.FORBIDDEN)


class KernelsDeleteViewTest(TestCase):

    def setUp(self):
        # upload kernel as user
        self.password = 'test1'
        self.user1 = User.objects.create_user('test1',
                                              'a@example.com',
                                              self.password)
        self.user2 = User.objects.create_user('test2',
                                              'a@example.com',
                                              self.password)
        self.image_hash = '93c795e321598d6d61403cb62ab30b8a1660bbc8'
        self.image_path = 'https://example.org/{0}/{1}.bin'
        self.image_path = self.image_path.format(self.image_hash[0:2],
                                                 self.image_hash)
        self.kernel = Kernel.objects.create(owner=self.user1,
                                            image_path=self.image_path,
                                            access_level=Kernel.ACCESS_PUBLIC)
        self.url = reverse('kernels:delete', kwargs={'pk': self.kernel.pk})

    def _login(self, user):
        login = self.client.login(username=user.username,
                                  password=self.password)
        self.assertTrue(login)
        return login

    def test_delete_get_self(self):
        self._login(self.user1)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'kernels/kernel_confirm_delete.html')

    def test_delete_get_other(self):
        # Forbidden
        self._login(self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, httplib.FORBIDDEN)

    def test_delete_get_anon(self):
        # Forbidden
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, httplib.FORBIDDEN)

    def test_delete_kernel_own(self):
        # Make sure user can delete their own kernel
        self._login(self.user1)
        pk = self.kernel.owner.pk
        response = self.client.post(self.url, {}, follow=True)
        self.assertRedirects(response, reverse('accounts:user-profile',
                                               kwargs={'pk': pk}))

    def test_delete_kernel_other(self):
        # Forbidden
        self._login(self.user2)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, httplib.FORBIDDEN)

    def test_delete_kernel_anon(self):
        # Forbidden
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, httplib.FORBIDDEN)


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
        # Make sure we have 3 kernels
        self.assertEqual(Kernel.objects.count(), 3)

    def _create_kernel(self, access_level):
        end = Kernel.ACCESS_LEVELS[access_level][0]
        image_hash = '93c795e321598d6d61403cb62ab30b8a1660bbc{0}'.format(end)
        image_path = 'https://example.org/{0}/{1}.bin'
        image_path = image_path.format(image_hash[0:2], image_hash)
        kernel = Kernel.objects.create(owner=self.user1,
                                       image_path=image_path,
                                       access_level=access_level)
        return kernel

    def _get_detail_url(self, pk):
        return reverse('kernels:view', kwargs={'pk': pk})

    def _assertViewable(self, kernel):
        # KernelsDetailView
        detail_url = self._get_detail_url(kernel.pk)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kernels/view.html')

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
