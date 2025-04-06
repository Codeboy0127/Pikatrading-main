from django.shortcuts import render, redirect
from datetime import datetime
from cart.forms import CheckoutForm
from cart.cart import Cart
from .models import Order, OrderItem
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
from django.shortcuts import get_object_or_404


# Generate PDF invoice from admin dashboard
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    print(order.first_name)
    html = render_to_string('order/invoice_order.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=INV-PK{order.created_at.year}{order.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(response)
    return response

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,'order/order_detail.html',{'order': order})

def start_order(request):
    cart = Cart(request)
    #Launch asyncronous task
    #order_created.delay('1')
    #test.apply_async(countdown=300)
    
    

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
            

            # Creating new order
            order = Order.objects.create(user=request.user, first_name=first_name, last_name=last_name, email=email, phone=phone, address=address, zipcode=zipcode, place=place, 
            first_name_billing=first_name_billing, last_name_billing=last_name_billing, address_billing=address_billing, zipcode_billing=zipcode_billing, place_billing=place_billing) 
            #order.total_amount = cart.get_total_cost()
            #order.save()
            
            cart_data = cart.get_all_products()
            #for item in cart:
            total_amount  = 0
            for item in cart_data:
                
                product = item['product']
                quantity = int(item['quantity'])
                price = product.get_display_price(request.user.id) * quantity
                total_amount = total_amount + price
                #OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity)
                OrderItem.objects.create(order=order, product=item['product'], price=item['total_price'], quantity=item['quantity'])
            order.total_amount = total_amount
            order.save()
            #order_created(order.id)
            #testA.apply_async(args=[order.id],countdown=300)
            #testB.apply_async(args=[order.id],countdown=120)
            request.session['order_id'] = {'id': order.id, 'payment_method':payment}  
            print(request.session.keys() )
            if payment == "creditcard" or payment == "creditcard-jut":
                return redirect('pay_creditcard')
            elif payment == "qr" or payment == "wechat":
                return redirect('pay_qrcode')
            elif payment == "alipay":
                return redirect('pay_alipay')
            else: 
                return redirect('checkout', {"form": form})
        else: # If the form validation is fail
            print('Invalid form submission')
            return redirect('checkout', {"form": form})
   
    else:
        form = CheckoutForm()
        return redirect('checkout', {"form": form})