from django.db import models
from django.contrib.auth.models import User


class ProfileManager(models.Manager):

    def get_profile(self, user=None):
        profile, created = self.get_or_create(user=user)
        if created:
            if user.first_name or user.last_name:
                profile.name = ' '.join([user.first_name, user.last_name])
            else:
                profile.name = user.username
            profile.save()
        return profile


class Profile(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=60, blank=True)
    web_site = models.URLField(blank=True)
    position = models.CharField(max_length=60, blank=True)
    affiliation = models.CharField(max_length=60, blank=True)
    instructor = models.CharField(max_length=60, blank=True)

    objects = ProfileManager()
