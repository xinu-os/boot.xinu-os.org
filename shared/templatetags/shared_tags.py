from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, url):
    current_url = context['request'].path
    # Blank URL is a special case since it matches everything
    if url != '/' and current_url.startswith(url):
        return 'active'
    elif url == current_url:
        return 'active'
    else:
        return ''
