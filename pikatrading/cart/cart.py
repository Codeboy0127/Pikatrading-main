from django.conf import settings
from django.shortcuts import get_object_or_404
from product.models import Product

class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        
        if request.user.is_authenticated:# Make usre that user is login before they add product to the cart
            self.user_id = request.user.id
        else:
            self.user_id = None

        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        
        self.cart = cart
    
    def __iter__(self):
        for p in self.cart.keys():
            self.cart[str(p)]['product'] = Product.objects.get(pk=p)
        for item in self.cart.values():
            item['total_price'] = int(item['product'].get_display_price(self.user_id) * item['quantity']) 

            yield item
    
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
    
    def save(self): # Notify server or browser that we have the modification
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True
    
    def add(self, product_id, quantity=1, update_quantity=False):
        product_id = str(product_id)

        if update_quantity:
            self.cart[product_id]['quantity'] += int(quantity)
            
            if self.cart[product_id]['quantity'] == 0:
                
                self.remove(product_id)
                
        else: # ordinary add scenarios (+1 increase)
            if product_id not in self.cart:
                self.cart[product_id] = {'quantity': quantity, 'id': product_id}
            else:
                self.cart[product_id]['quantity'] += quantity
                

        self.save() # Update the session
    
    def remove(self, product_id):
        
        if str(product_id) in self.cart:
            
            del self.cart[str(product_id)]
            self.save()
            
    
    def get_total_cost(self):
        for p in self.cart.keys():
            self.cart[str(p)]['product'] = Product.objects.get(pk=p)

        return int(sum(item['product'].get_display_price(self.user_id) * item['quantity'] for item in self.cart.values())) 
    
    def get_item(self, product_id):
        if str(product_id) in self.cart:
            return self.cart[str(product_id)]
        else:
            
            return None
    def get_all_products(self):
        products = []
        for product_id, item_data in self.cart.items():
            product = get_object_or_404(Product, pk=int(product_id))
            products.append({
                'product': product,
                'quantity': item_data['quantity'],
                'total_price': int(product.get_display_price(self.user_id) * item_data['quantity']),
            })

        return products
        
    def get_current_quantity(self, product_id):
        """
        Get the current quantity of the product in the cart.
        """
        if str(product_id) in self.cart:
            return self.cart[str(product_id)]['quantity']
        return 0
        