from django.forms import ModelForm

from accounts.models import Profile


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']
