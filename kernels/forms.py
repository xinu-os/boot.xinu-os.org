from django import forms

from kernels.models import Kernel


class KernelUploadForm(forms.ModelForm):
    class Meta:
        model = Kernel
