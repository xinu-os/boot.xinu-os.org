from django import forms

from kernels.models import Kernel


class KernelUploadForm(forms.ModelForm):
    def __init__(self, **kwargs):
        self.owner = kwargs.pop('owner', None)
        initial = kwargs.setdefault('initial', {})
        initial.update({'owner': self.owner})
        super(KernelUploadForm, self).__init__(**kwargs)

    def save(self, commit=True):
        obj = super(KernelUploadForm, self).save(commit=False)
        obj.owner = self.owner
        if commit:
            obj.save()
        return obj

    class Meta:
        model = Kernel
        exclude = ['owner', 'checksum']
