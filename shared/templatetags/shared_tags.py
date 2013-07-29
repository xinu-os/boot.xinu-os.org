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


@register.filter
def anti_spam(value):
    value = value.replace('@', ' {at} ')
    value = value.replace('.', ' {dot} ')
    value = value.replace('+', ' {plus} ')
    value = value.replace('-', ' {dash} ')
    return value
