from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, CreateView

from boot.lib.views import ProtectedMixin
from kernels.models import Kernel
from kernels.forms import KernelUploadForm


class KernelsUploadView(ProtectedMixin, CreateView):
    form_class = KernelUploadForm
    template_name = 'kernels/upload.html'

    def get_form_kwargs(self):
        kwargs = super(KernelsUploadView, self).get_form_kwargs()
        kwargs.update({'owner': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse('kernels:view', kwargs={'pk': self.object.pk})

    def post(self, request, *args, **kwargs):
        # Cannot upload with other user as owner
        self.kwargs['pk'] = request.POST['owner']
        if not ProtectedMixin.is_my_account(self):
            raise PermissionDenied
        return super(KernelsUploadView, self).post(request, *args, **kwargs)


class KernelsImageView(DetailView):
    model = Kernel
    template_name = 'kernels/view.html'
