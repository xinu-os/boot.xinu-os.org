from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class ProtectedMixin(object):

    @staticmethod
    def is_my_account(obj):
        """Check if the Django CBV user is the same as the request."""
        return obj.request.user.pk == int(obj.kwargs['pk'])

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """Prevent users that are not logged in from seeing this view."""
        return super(ProtectedMixin, self).dispatch(*args, **kwargs)
