from django import template

register = template.Library()


@register.filter
def space_thousands(value):
    try:
        value = str(value).replace(',', '.')
        value = int(float(value))
        return f'{value:,}'.replace(',', ' ')
    except (ValueError, TypeError):
        return value