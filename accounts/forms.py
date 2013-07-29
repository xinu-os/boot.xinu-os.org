from django import forms

from accounts.models import Profile


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(label='Email', max_length=30)

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = self.instance.user.email
        self.fields.keyOrder = [
            'name',
            'email',
            'web_site',
            'affiliation',
            'position',
            'instructor',
        ]

    def save(self, *args, **kwargs):
        super(ProfileForm, self).save(*args, **kwargs)
        self.instance.user.email = self.cleaned_data.get('email')
        self.instance.user.save()

    class Meta:
        model = Profile
        exclude = ['user']
