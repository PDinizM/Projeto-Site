from django import template

register = template.Library()


@register.filter
def retornar_dc(valor):
    try:
        valor = float(valor)
    except (ValueError, TypeError):
        return ""

    if valor == 0:
        return ""
    elif valor > 0:
        return "D"
    else:
        return "C"


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0.00)
