from django import template
from ..models import Product

register = template.Library()

# Template tag to get the value #
@register.simple_tag
def get_price(product_id, user_id):
    product = Product.objects.get(id = product_id) 
    print(product.get_display_price(user_id))
    return product.get_display_price(user_id)

@register.simple_tag
def get_quantity(product_id, user_id):
    product = Product.objects.get(id = product_id) 
    #print(product.get_display_price(user_id))
    return product.get_min_quantity(user_id)
    
# Filter to get the value #
@register.filter
def get_min_quantity(product_id, user_id):
    product = Product.objects.get(id = product_id) 
    return product.get_min_quantity(user_id)

    

