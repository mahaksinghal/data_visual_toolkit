from django import template

register = template.Library()

@register.filter
def filesizeformat(value):
    # converts a file size in bytes to a human-readable format.
    if value < 1024:
        return f'{value} bytes'
    elif value < 1024 * 1024:
        return f'{value / 1024:.2f} KB'
    elif value < 1024 * 1024 * 1024:
        return f'{value / (1024 * 1024):.2f} MB'
    else:
        return f'{value / (1024 * 1024 * 1024):.2f} GB'