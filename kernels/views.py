from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.utils import simplejson as json
from django.views.generic import DetailView, CreateView, DeleteView

from shared.views import ProtectedMixin
from kernels.models import Kernel
from kernels.forms import KernelUploadForm


class KernelProtectedMixin(object):
    def is_private(self, kernel):
        not_private = (kernel.access_level != Kernel.ACCESS_PRIVATE)
        is_users = (kernel.owner == self.request.user)
        if not_private or is_users:
            return False
        return True


class KernelsUploadView(ProtectedMixin, CreateView):
    form_class = KernelUploadForm
    template_name = 'kernels/upload.html'

    def get_form_kwargs(self):
        kwargs = super(KernelsUploadView, self).get_form_kwargs()
        kwargs.update({'owner': self.request.user})
        kwargs.update({'parent': None})
        return kwargs

    def get_success_url(self):
        return reverse('kernels:view', kwargs={'pk': self.object.pk})

    def post(self, request, *args, **kwargs):
        # Cannot upload with other user as owner
        self.kwargs['pk'] = request.POST['owner']
        if not ProtectedMixin.is_my_account(self):
            raise PermissionDenied
        return super(KernelsUploadView, self).post(request, *args, **kwargs)


class KernelsView(DetailView, KernelProtectedMixin):
    model = Kernel
    template_name = 'kernels/view.html'

    def dispatch(self, request, *args, **kwargs):
        if self.is_private(self.get_object()):
            raise PermissionDenied
        # Ajax response just needs to tell the JS client to redirect
        if request.is_ajax():
            response = {'redirect': request.path_info}
            return HttpResponse(json.dumps(response),
                                content_type='application/json')
        return super(KernelsView, self).dispatch(request, *args, **kwargs)


class KernelsDeleteView(DeleteView):
    model = Kernel
    success_url = reverse_lazy('accounts:profile')

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != self.request.user:
            raise PermissionDenied
        return super(KernelsDeleteView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != self.request.user:
            raise PermissionDenied
        return super(KernelsDeleteView, self).post(request, *args, **kwargs)
