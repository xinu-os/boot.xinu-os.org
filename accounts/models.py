from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=60, blank=True)
    web_site = models.URLField(blank=True)
    position = models.CharField(max_length=60, blank=True)
    affiliation = models.CharField(max_length=60, blank=True)
    instructor = models.CharField(max_length=60, blank=True)
