from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .cart import Cart
from product.models import Product
from django.contrib import messages
from .forms import CheckoutForm
from order.models import Order, OrderItem, ShippingRate
from order.views import admin_order_pdf
from payment.tasks import send_html_email
from django.conf import settings
from decimal import Decimal
from django.utils import timezone


### LINE NOTIFICATION ORDER TEMPLATE###
MESSAGE_TEMPLATE = """NEW ORDER: ID = @OrderID \n Date: dd/mm/yyyy \n ---------- \n
1. @ProductName[@SKU] @Price บาท x @Qantity = TotalPrice1 \n 1. @ProductName[@SKU] @Price บาท x @Qantity = TotalPrice2 \n 
Total: @Total Amount \n---------- \n
Customer\n
Name: @FirstName @Lastname\n
Address: @Address\n
City/Place: @City\n
Zipcode: @Zipcode\n
Email: @Email\n
Phone: @PhoneNumber\n
"""


# Create your views here.
@login_required
def add_to_cart(request, product_id):
    quantity = int(request.GET.get('quantity', 1))
    product = Product.objects.get(pk=product_id)
    #print("quantity, JA : "+ str(quantity))
    cart = Cart(request)
    current_quantity = cart.get_current_quantity(product_id)
    #print("current quantity : "+ str(current_quantity))
    if current_quantity + quantity <= product.stock:
        cart.add(product_id,quantity)
    
    return render(request, 'cart/menu_cart.html')
   
@login_required
def cart(request):
    return render(request, 'cart/cart.html')

def update_cart(request, product_id, action):
    cart = Cart(request)
    product = Product.objects.get(pk=product_id)
    quantity = int(request.GET.get('quantity', 1))
    min_quantity = product.get_min_quantity(request.user.id)
    
    if action == 'increment':
        cart.add(product_id, 1, True)
    
    elif action == 'remove':
        
        cart.remove(product_id)      

    else:# decrement
        # If quantity is zero remove product from the page as well
        if quantity - 1 < min_quantity:
            response = render(request, 'cart/partials/cart_item.html', {'item': item})
            response['HX-Trigger'] = 'update-menu-cart'
            return response
        else:
            cart.add(product_id, -1, True)
    
   
    if cart.get_item(product_id):
        
        quantity = cart.get_item(product_id)['quantity']
    else:
        quantity = None
        
    if quantity:
        
        item = {
            'product': {
                'id': product.id,
                'name': product.name,
                'image': product.image,
                'get_thumbnail': product.get_thumbnail(),
                'price': product.get_display_price(request.user.id),
                'stock': product.stock,
            },
            'total_price': quantity * product.get_display_price(request.user.id),
            'quantity': quantity,
        }
    else:
        
        item = None
    
    #response = render(request, 'cart/cart.html')
    response = render(request, 'cart/partials/cart_item.html', {'item': item})
    response['HX-Trigger'] = 'update-menu-cart' # Trigger update menu cart ('update-menu-cart' in hx-trigger="update-menu-cart from:body") with response header of base.html
    
    return response


@login_required
def checkout(request):
    cart = Cart(request)
    #Launch asyncronous task
    #order_created.delay('1')
    #test.apply_async(countdown=300)
    #send_line_push_message.apply_async(args=[MESSAGE_TEMPLATE],countdown=1)
    #send_line_push_message(MESSAGE_TEMPLATE)
    #send_html_email("TESTOOO",20)   

    #print(admin_order_pdf(request,20))

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid(): # If the information in the form is correct

            ## SHIPPING INFOMRATION ##
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            address = request.POST.get('address')
            zipcode = request.POST.get('zipcode')
            place = request.POST.get('place')

            ## BILLING INFOMRATION ##
            same_as_shipping_flag = request.POST.get('same_as_shipping')
            
            if same_as_shipping_flag == 'yes':
                first_name_billing = first_name
                last_name_billing = last_name
                address_billing = address
                zipcode_billing = zipcode
                place_billing = place

            else:
                first_name_billing = request.POST.get('first_name_billing')
                last_name_billing = request.POST.get('last_name_billing')
                address_billing = request.POST.get('address_billing')
                zipcode_billing = request.POST.get('zipcode_billing')
                place_billing = request.POST.get('place_billing')


            ## PERSONEL INFORMATION ##
            phone = request.POST.get('phone')
            email = request.POST.get('email')

            ## PAYMENT METHOD
            payment = request.POST.get('payment_method')
            
            ## Shipping Method
            shipping_method = request.POST.get('shipping')

            



            # Creating new order
            order = Order.objects.create(user=request.user, first_name=first_name, last_name=last_name, email=email, phone=phone, address=address, zipcode=zipcode, place=place, 
            first_name_billing=first_name_billing, last_name_billing=last_name_billing, address_billing=address_billing, zipcode_billing=zipcode_billing, place_billing=place_billing) 
            #order.total_amount = cart.get_total_cost()
            #order.save()
            # CUSTOM ORDER ID
            current_date = timezone.now().date()
            order.order_id = 'PK' + str(current_date.year) + f"{current_date.month:02d}" + f"{order.id:04d}"

            cart_data = cart.get_all_products()
            #for item in cart:
            total_amount  = 0
            total_weight = 0
            for item in cart_data:
                
                product = item['product']
                quantity = int(item['quantity'])
                price = product.get_display_price(request.user.id) * quantity
                total_amount = total_amount + price
                weight = quantity * product.weight
                total_weight = total_weight + weight
                #OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity)
                OrderItem.objects.create(order=order, product=item['product'], price=product.get_display_price(request.user.id), quantity=item['quantity'],total_amount = price)
            
            # Store order total cost, shipping cost and vat
            order.product_amount = total_amount
            order.vat = round(total_amount * 0.07,2)
            order.product_amount_bf_tax = total_amount - round(total_amount * 0.07,2)
            order.shipping_method = shipping_method
            order.shipping_cost = calculate_shipping_cost(total_weight, shipping_method)
            order.total_amount = Decimal(total_amount) + calculate_shipping_cost(total_weight, shipping_method)
            
            order.save()
            #order_created(order.id)
            #testA.apply_async(args=[order.id],countdown=300)
            #testB.apply_async(args=[order.id],countdown=120)
            request.session['order_id'] = {'id': order.id, 'payment_method':payment}  
            print(request.session.keys() )

            # Use power of captian to get through winning victory
            if settings.CAPTIAN_KERORO_BYPASS ==1:
                return redirect('payment_result_keroro')

            if payment == "creditcard" or payment == "creditcard-jut":
                return redirect('pay_creditcard')
            elif payment == "qr" or payment == "wechat":
                return redirect('pay_qrcode')
            elif payment == "alipay":
                return redirect('pay_alipay')
            else: 
                return render(request, "cart/checkout.html", {"form": form, "total_amount":cart.get_total_cost() + calculate_shipping_cost(total_weight),'shipping_cost': calculate_shipping_cost(total_weight),'shipping_method':"thailandpost"})
        else: # If the form validation is fail
            messages.error(request, "There were errors in your submission. Please check the fields below.")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

                    #messages.error(request, error)
            cart_data = cart.get_all_products()
            total_weight = 0
            for item in cart_data:
                product = item['product']
                quantity = int(item['quantity'])
                weight = quantity * product.weight
                total_weight = total_weight + weight
            # Get the first error message
            #first_field, first_error_list = next(iter(form.errors.items()))
            #first_error = first_error_list[0]  # Get the first error message
            #messages.error(request, f"{first_field.capitalize()}: {first_error}")
            print('Invalid form submission')
            return render(request, "cart/checkout.html", {"form": form,"total_amount":cart.get_total_cost() + calculate_shipping_cost(total_weight),'shipping_cost': calculate_shipping_cost(total_weight),'shipping_method':"thailandpost"})
   
    else:
        form = CheckoutForm()
        cart_data = cart.get_all_products()
        total_weight = 0
        for item in cart_data:
            product = item['product']
            quantity = int(item['quantity'])
            weight = quantity * product.weight
            total_weight = total_weight + weight

        return render(request, "cart/checkout.html", {"form": form, "total_amount":cart.get_total_cost() + calculate_shipping_cost(total_weight),'shipping_cost': calculate_shipping_cost(total_weight),'shipping_method':"thailandpost"})

def hx_menu_cart(request):
    return render(request, 'cart/menu_cart.html')

def hx_cart_total(request):
    return render(request, 'cart/partials/cart_total.html')

def hx_cost_summary_checkout(request):
    if request.method == "POST":
        cart = Cart(request)
        cart_data = cart.get_all_products()
        total_weight = 0
        for item in cart_data:
            product = item['product']
            quantity = int(item['quantity'])
            weight = quantity * product.weight
            total_weight = total_weight + weight

        selected_shipping = request.POST.get("shipping") 
        print('selected shipping method: ', selected_shipping)
    return render(request, 'cart/partials/cost_summary_checkout.html', {"total_amount":cart.get_total_cost() + calculate_shipping_cost(total_weight,selected_shipping),'shipping_cost': calculate_shipping_cost(total_weight,selected_shipping), 'shipping_method':selected_shipping})

def calculate_shipping_cost(weight, shipping_method = "thailandpost"):
    if shipping_method == "thailandpost":
        rate = ShippingRate.objects.filter(
            min_weight__lte=weight,
            max_weight__gte=weight
        ).first()
        return rate.rate if rate else 1000  # Default to 1000 if no rate found
    else:
        return 0