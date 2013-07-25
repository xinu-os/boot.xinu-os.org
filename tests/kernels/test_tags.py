from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.test import TestCase

from kernels.templatetags import kernel_tags
from kernels.models import Kernel


class KernelsUserKernelsTagTestCase(TestCase):
    def setUp(self):
        # two users, user 1 has 3 images
        self.user1 = User.objects.create_user('a', 'a@example.com', 'z')
        self.user2 = User.objects.create_user('b', 'b@example.com', 'y')
        # images
        self.kernel0 = self._create_kernel(self.user1, Kernel.ACCESS_PUBLIC)
        self.kernel1 = self._create_kernel(self.user1, Kernel.ACCESS_LINK)
        self.kernel2 = self._create_kernel(self.user1, Kernel.ACCESS_PRIVATE)
        # Crate a fourth kernel owned by user2
        self.kernel3 = self._create_kernel(self.user2, Kernel.ACCESS_PUBLIC)

    def _create_kernel(self, user, access_level):
        f = ContentFile(Kernel.ACCESS_LEVELS[access_level][1])
        f.name = 'access_file'
        kernel = Kernel.objects.create(owner=user,
                                       image=f,
                                       access_level=access_level)
        return kernel

    def _assertQuerysetEqual(self, actual, expected):
        """Make sure all elements in a queryset are equal.

        I couldn't get the actual function to work, bad transform?"""
        for a, e in zip(actual, expected):
            self.assertEqual(a, e)

    def test_bad_context(self):
        context = {}
        viewer = self.user1
        tag_ctx = kernel_tags.user_kernels(context, viewer)
        actual = tag_ctx['kernels']
        expected = Kernel.objects.filter(owner=self.user1)
        self._assertQuerysetEqual(actual, expected)

    def test_with_self(self):
        # Self user should see all public/linkable/private kernels
        # object is the user page we're looking at,
        # viewer is the user viewing the page
        context = {'object': self.user1}
        viewer = self.user1
        tag_ctx = kernel_tags.user_kernels(context, viewer)
        actual = tag_ctx['kernels']
        expected = Kernel.objects.filter(owner=self.user1)
        self._assertQuerysetEqual(actual, expected)

    def test_with_other(self):
        # Other user should see all public kernels only
        context = {'object': self.user1}
        viewer = self.user2
        tag_ctx = kernel_tags.user_kernels(context, viewer)
        actual = tag_ctx['kernels']
        expected = Kernel.objects.filter(owner=self.user1,
                                         access_level=Kernel.ACCESS_PUBLIC)
        self._assertQuerysetEqual(actual, expected)

    def test_with_no_user(self):
        # Anonymous User should see all public kernels only
        context = {'object': self.user1}
        viewer = None
        tag_ctx = kernel_tags.user_kernels(context, viewer)
        actual = tag_ctx['kernels']
        expected = Kernel.objects.filter(owner=self.user1,
                                         access_level=Kernel.ACCESS_PUBLIC)
        self._assertQuerysetEqual(actual, expected)