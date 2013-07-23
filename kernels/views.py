from django.views.generic import DetailView, CreateView

from kernels.models import Kernel
from kernels.forms import KernelUploadForm


class KernelsUploadView(CreateView):
    form_class = KernelUploadForm
    template_name = 'kernels/upload.html'


class KernelsImageView(DetailView):
    model = Kernel
    template_name = 'kernels/view.html'
