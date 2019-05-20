from django import template

register = template.Library()

@register.simple_tag
def is_video_path(path):
    if path == '/videos' or path.startswith('/video/'):
        return 'active'

    return ''

@register.simple_tag
def is_user_path(path):
    if path == '/user_account' or path.startswith('/profile/'):
        return 'active'

    return ''
