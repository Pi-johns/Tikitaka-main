from django import template
import math

register = template.Library()

@register.filter
def get_item(container, key):
    # Handle dictionary
    if isinstance(container, dict):
        return container.get(key)
    # Handle list (by index)
    elif isinstance(container, list) and isinstance(key, int):
        try:
            return container[key]
        except IndexError:
            return None
    return None
@register.filter
def get_rating_count(products_with_ratings_info, product_id):

    for item in products_with_ratings_info:
        if isinstance(item, dict) and item.get('product').id == product_id:
            return item.get('rating_count', 0)
    return 0

@register.filter
def multiply(value, arg):
    """Multiply the value by the arg"""
    return float(value) * float(arg)

@register.filter
def readtime(wordcount):
    # Average reading speed: 200 words per minute
    minutes = math.ceil(wordcount / 200)
    return f"{minutes} min read"

@register.filter
def dict_get(d, key):
    return d.get(key)