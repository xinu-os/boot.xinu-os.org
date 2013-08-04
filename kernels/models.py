from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _


class Kernel(models.Model):
    # Location to store kernel images
    IMAGE_PATH = 'kernels'
    # Access levels for kernel
    ACCESS_PUBLIC = 0
    ACCESS_LINK = 1
    ACCESS_PRIVATE = 2
    ACCESS_LEVELS = (
        (ACCESS_PUBLIC, _('Public')),
        (ACCESS_LINK, _('Link only')),
        (ACCESS_PRIVATE, _('Private')),
    )

    checksum = models.CharField(max_length=40, primary_key=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    owner = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now=True)
    image_path = models.URLField("Kernel Image Source")
    access_level = models.SmallIntegerField(choices=ACCESS_LEVELS, default=0)

    def save(self, *args, **kwargs):
        last = self.image_path.split('/')[-1]
        self.checksum, _ = last.split('.')
        return super(Kernel, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Kernel({0}, {1}, {2})'.format(self.owner,
                                              self.access_level,
                                              self.checksum)
