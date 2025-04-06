from django.shortcuts import render,get_object_or_404
from .models import Product
from django.http import JsonResponse



# Create your views here.
def product(request,slug):
    
    product  = get_object_or_404(Product, slug=slug, is_published=True)
    #if request.user.is_authenticated:
    #    user_id = request.user.id
    #else:
    #    user_id = None
    return render(request, 'product/product.html',{'product':product})


