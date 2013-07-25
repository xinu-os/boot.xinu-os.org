from django import template

from kernels.models import Kernel

register = template.Library()


@register.inclusion_tag('kernels/includes/kernels_list.html',
                        takes_context=True)
def user_kernels(context, viewer):
    """Given the user associated with the `context`, generate the kernels
    that the `viewer` is able to see."""
    profile_user = context['object']
    kernels = Kernel.objects.filter(owner=profile_user)
    if viewer != profile_user:
        kernels = kernels.filter(access_level=Kernel.ACCESS_PUBLIC)
    return {'kernels': kernels}
