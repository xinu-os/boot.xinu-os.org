from django import template

from kernels.models import Kernel

register = template.Library()


@register.inclusion_tag('kernels/includes/kernels_list.html',
                        takes_context=True)
def user_kernels(context, viewer):
    """Given the user associated with the `context`, generate the kernels
    that the `viewer` is able to see."""
    kernels = Kernel.objects.all()
    try:
        profile_user = context['object']
        kernels = kernels.filter(owner=profile_user)
    except KeyError:
        profile_user = None
    if viewer != profile_user:
        kernels = kernels.filter(access_level=Kernel.ACCESS_PUBLIC)
    context.update({'header': 'Available Kernels',
                    'kernels': kernels})
    return context


@register.inclusion_tag('kernels/includes/kernels_list.html',
                        takes_context=True)
def all_kernels(context):
    """Show all public kernels."""
    kernels = Kernel.objects.filter(access_level=Kernel.ACCESS_PUBLIC)
    context = {}
    context.update({'header': 'Public Kernels',
                    'kernels': kernels,
                    'show_owner': True})
    return context
