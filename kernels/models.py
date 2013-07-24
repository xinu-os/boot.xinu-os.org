from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _


class Kernel(models.Model):
    # Location to store kernel images
    IMAGE_PATH = 'kernels'
    # Access levels for kernel
    ACCESS_LEVELS = (
        (0, _('Public')),
        (1, _('Link only')),
        (2, _('Private')),
    )

    checksum = models.CharField(max_length=40, primary_key=True)
    owner = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now=True)
    image = models.FileField(upload_to=IMAGE_PATH)
    access_level = models.SmallIntegerField(choices=ACCESS_LEVELS, default=0)

    def save(self, *args, **kwargs):
        self.checksum = '0'*40
        super(Kernel, self).save(*args, **kwargs)
