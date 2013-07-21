from django.contrib import admin
from accounts.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    pass
admin.site.register(Profile, ProfileAdmin)
