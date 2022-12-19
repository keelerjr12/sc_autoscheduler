from django import template

register = template.Library()

@register.filter
def parse_org(value):
    if value == None:
        return ''
    
    return value

@register.filter
def parse_qual(value):
    if value == 1:
        return 'X'
    
    return ''