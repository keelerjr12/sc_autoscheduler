from django import template

register = template.Library()

@register.filter()
def lookup(value, arg):
    return value[arg]