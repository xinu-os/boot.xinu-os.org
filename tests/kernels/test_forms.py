import logging
logging.disable(logging.WARNING)

from django.test import TestCase
from django.contrib.auth.models import User

from kernels.models import Kernel
from kernels.forms import KernelUploadForm


class KernelUploadFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('a', 'b@example.org', 'c')

    def test_kernel_upload_form_no_save(self):
        kuf = KernelUploadForm(owner=self.user)
        kuf.save(commit=False)
        kernels = Kernel.objects.all()
        # since we did not commit, it should not be in db
        self.assertEqual(kernels.count(), 0)
