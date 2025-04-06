import requests
from django.shortcuts import render, redirect
from cart.cart import Cart
from order.models import Order
from django.conf import settings
from .tasks import order_created,qr_transaction_inquiry, cd_transaction_inquiry
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponse
import hashlib
import json
from django.contrib import messages


header = {
            'content-type': 'application/json',
            'x-api-key': settings.KBANK_SKEY
        }

# Create your views here.

def validate_stock(order):
    """Validate that all products in cart have sufficient stock"""
    
    for item in order.items.all():
        product = item.product
        quantity = item.quantity
        
        if product.stock < quantity:
            return False
    
    return True

def creditcard_payment(request):
    payment_method = request.session.get('order_id',None)['payment_method']
    MID = settings.KBANK_MID[payment_method]
    order_id = request.session.get('order_id',None)
    order = Order.objects.get(id = order_id['id'])

    # Validate stock before creating order
    if not validate_stock(order):
        cart = Cart(request)
        cart_data = cart.get_all_products()    
        # Check stock availability for each item
        for item in cart_data:
            
            product = item['product']
            if product.stock <  int(item['quantity']):
                # If stock is insufficient, remove item from cart
                cart.remove(product.id)
                messages.warning(request, f'"{product.name}" has been removed from your cart due to insufficient stock.')
        
        return redirect('cart')

    #MID = settings.KBANK_MID(payment_method)
    #print(payment_method)
    #print(MID)
    return render(request, 'payment/payment_process_creditcard.html', {'KBANK_EMBEBED_URL':settings.KBANK_EMBEDED_URL,'KBANK_PKEY': settings.KBANK_PKEY,'MID' : MID, "total_amount": str(order.total_amount)})

def qrcode_payment(request):
    cart = Cart(request)
    order_id = request.session.get('order_id',None)
    order = Order.objects.get(id = order_id['id'])
    
    #print(order_id['id'])
    # Validate stock before creating order
    if not validate_stock(order):
        cart = Cart(request)
        cart_data = cart.get_all_products()    
        # Check stock availability for each item
        for item in cart_data:
            
            product = item['product']
            if product.stock <  int(item['quantity']):
                # If stock is insufficient, remove item from cart
                cart.remove(product.id)
                messages.warning(request, f'"{product.name}" has been removed from your cart due to insufficient stock.')
        
        return redirect('cart')
   
    url = settings.KBANK_ORDER_URL
    payload = {
            'amount': str(order.total_amount),
            'currency': 'THB',
            'description': 'Payment submission',
            'source_type': order_id['payment_method'],
            'reference_order': order_id['id']# using dummy for now and will be replace by oder_id
                        
        }
    r = requests.post(url, json = payload, headers = header )
    response_data = r.json()
    #print(response_data['id'])
    #print(r.status_code)
    #print(r.text)
    
    #order.total_amount = cart.get_total_cost()
    order.payment_method = order_id['payment_method']
    order.kbank_order_id = response_data['id']
    order.save()
    return render(request, 'payment/payment_process_qrcode.html',{'KBANK_EMBEBED_URL':settings.KBANK_EMBEDED_URL,'KBANK_PKEY': settings.KBANK_PKEY, 'payment_method': order_id['payment_method'], 'payment_id' : response_data['id'],"total_amount": str(order.total_amount)})

def alipay_payment(request):
    cart = Cart(request)
    order_id = request.session.get('order_id',None)
    order = Order.objects.get(id = order_id['id'])

    # Validate stock before creating order
    if not validate_stock(order):
        cart = Cart(request)
        cart_data = cart.get_all_products()    
        # Check stock availability for each item
        for item in cart_data:
            
            product = item['product']
            if product.stock <  int(item['quantity']):
                # If stock is insufficient, remove item from cart
                cart.remove(product.id)
                messages.warning(request, f'"{product.name}" has been removed from your cart due to insufficient stock.')
        
        return redirect('cart')
    
    url = settings.KBANK_CHARGE_URL

    payload = {
            'amount': str(order.total_amount),
            'currency': 'THB',
            'description': 'Payment submission',
            'source_type': order_id['payment_method'],
            'reference_order': order_id['id'],# using dummy for now and will be replace by oder_id
            #'dcc_data': { 'dcc_currency':dcc_currency},
            'customer': { 'customer_id':request.user.id},
            #'additional_data': { 'mid':'401662304111001'}
                                      
        }

    r = requests.post(url, json = payload, headers = header )
    response_data = r.json()
    #print(r.status_code)
    #print(r.text)
    #print(response_data['transaction_state'])
    #print(response_data['status'])
    if response_data['transaction_state'] == 'Initialize' and response_data['status'] == 'success':
        
        order.payment_method = order_id['payment_method']
        order.kbank_charge_id = response_data['id']
        order.save()
        return redirect(response_data['redirect_url'])

    return redirect('cart')



def payment_process(request):

    if request.method == 'POST':
        token = request.POST.get('token')
        dcc_currency = request.POST.get('dcc_currency')
        mid = request.POST.get('mid')
        payment_method =  request.POST.get('paymentMethods')
        smartpay_id =  request.POST.get('smartpayId')
        term =  request.POST.get('term')
        url = settings.KBANK_CHARGE_URL
        amount = str(request.POST.get('total_amount'))
        
        # Store token in database where it will be used in callback of credit card result page
        order_id = request.session.get('order_id',None)
        order = Order.objects.get(id = order_id['id'])

         # Validate stock before creating order
        if not validate_stock(order):
            cart = Cart(request)
            cart_data = cart.get_all_products()    
            # Check stock availability for each item
            for item in cart_data:
            
                product = item['product']
                if product.stock <  int(item['quantity']):
                    # If stock is insufficient, remove item from cart
                    cart.remove(product.id)
                    messages.warning(request, f'"{product.name}" has been removed from your cart due to insufficient stock.')
        
        return redirect('cart')

        order.payment_method = order_id['payment_method']
        #order.total_amount = amount
        order.kbank_token_id = token
        order.save()
        #print('WTF')
        #print(token)
        #print(payment_method)
        #print(amount)
        #print('order id = ', order_id['id'])
        #print(smartpay_id)
        #print(term)
        #header = {
           # 'content-type': 'application/json',
           #'x-api-key': 'skey_test_21650lWfhwUJzDvZhblv0Y0DPHl0GtPTR4Ay2'
        #}

        payload = {
            'amount': amount,
            'currency': 'THB',
            'description': 'Payment submission',
            'source_type': payment_method,
            'mode': 'token',
            'reference_order': order_id['id'],# using dummy for now and will be replace by oder_id
            'token': token,
            'dcc_data': { 'dcc_currency':dcc_currency},
            'customer': { 'customer_id':request.user.id},
            'additional_data': { 'mid':mid,
                                  'smartpay_id':smartpay_id,
                                  'term':term
            }
            
        }
        
        r = requests.post(url, json = payload, headers = header )
        response_data = r.json()
        # Store Charge ID from kbank in Database
        order.kbank_charge_id = response_data['id']
        order.save()
        #print(r.status_code)
        #print(r.text)
        #print(response_data['redirect_url'])
        #except Exception as e:
            #print('fail ja')
    
        return redirect(response_data['redirect_url'])

    return redirect('cart')






################################# PAYMENT LANDING PAGE RESULT ###############################################

@csrf_exempt
def payment_result_cd(request):
    
    # Relogin for user who submitted the payment
    token = request.POST.get('token') # get token from Kbank
    #print(token)
    order = Order.objects.get(kbank_token_id = token)
    #print(order.user.id)
    user = User.objects.get(pk=order.user.id)
    # Ensure the user is authenticated using Allauth's backend
    user.backend = 'allauth.account.auth_backends.AuthenticationBackend'
    login(request, user)
    cd_transaction_inquiry.apply_async(args=[order.id],countdown=600)
    #print('creditcard Result:' + request.POST.get('status'))
    
    # Remove the cart from the session
    if 'cart' in request.session:
        del request.session['cart']

    return render(request, 'payment/payment_result_cd.html')


@csrf_exempt
def payment_result_ali(request):
    
    # Relogin for user who submitted the payment
    charge_id = request.POST.get('objectId') # get charge id from Kbank
    #print(token)
    order = Order.objects.get(kbank_charge_id = charge_id)
    #print(order.user.id)
    user = User.objects.get(pk=order.user.id)
    user.backend = 'allauth.account.auth_backends.AuthenticationBackend'
    login(request, user)
    cd_transaction_inquiry.apply_async(args=[order.id],countdown=600)
    #print('creditcard Result:' + request.POST.get('status'))

    # Remove the cart from the session
    if 'cart' in request.session:
        del request.session['cart']
    
    return render(request, 'payment/payment_result_cd.html')

  
def payment_result_qr(request):
    
    order_id = request.session.get('order_id',None)
    order = Order.objects.get(id = order_id['id'])
    if order_id['payment_method'] == 'qr' or  order_id['payment_method'] == 'wechat':
        #order.kbank_charge_id = request.POST.get('chargeId')
        #order.save()
        qr_transaction_inquiry.apply_async(args=[order.id],countdown=600)
        #print('QR Result:' + request.POST.get('chargeId'))
        
    # Remove the cart from the session
    if 'cart' in request.session:
        del request.session['cart']
    
    return render(request, 'payment/payment_result_qr.html')

def payment_result_keroro(request):
    order_id = request.session.get('order_id',None)
    order = Order.objects.get(id = order_id['id'])

    # UPPDATE ORDER DETAIL#
    order.status = 'process'
    order.paid = False
    order.notify = True
    order.paid_amount = 0
    order.kbank_charge_id = 'KERORO'
    order.save()

    # SEND THE EMAIL AND LINE NOTIFIATION #
    order_created.delay(int(order_id['id']))
    
    # Remove the cart from the session
    if 'cart' in request.session:
        del request.session['cart']
    
    return render(request, 'payment/payment_result_qr.html')    

################################# NOTIFICATION FROM KBANK ###############################################

@csrf_exempt
def payment_qr_notify(request):

    if request.method == 'POST':
        #Convert body of post request into json format
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        
        # Get parameter to calculate Checksum
        order_id = int(body['reference_order'])
        order = Order.objects.get(id = order_id)
        charge_id = body['id'] # Use body of id as an representative of charge id
        amount = format(order.total_amount, '.4f') 
        currency = "THB"
        status =  body['status'] # "success" or "fail"
        transaction_state = body['transaction_state']
        text_builder = charge_id + amount + currency + status + transaction_state + settings.KBANK_SKEY
        #print(text_builder)
        text_builder_hash = hashlib.sha256(text_builder.encode('utf-8')).hexdigest()
        #print(text_builder_hash)
        checksum = body['checksum']
        #print(checksum)
        # If checksum is equal to the store information, Then update order status, amount, notify and send the email out
        if text_builder_hash == checksum:
            order.status = 'process'
            order.paid = True
            order.notify = True
            order.paid_amount = body['amount']
            order.kbank_charge_id = charge_id
            order.save()
            order_created.delay(order_id)
            return HttpResponse(status=200)
        else:
            order.status = 'paymentfail'
            order.paid = False
            return 'nothing'   
    
    return 'nothing'

@csrf_exempt
def payment_cd_notify(request):

    if request.method == 'POST':
        
        #Convert body of post request into json format
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        
        # Get parameter to calculate Checksum
        order_id = int(body['reference_order'])
        order = Order.objects.get(id = order_id)
        charge_id = order.kbank_charge_id # use charge id from response of charge api
        
        amount = format(order.total_amount, '.4f') 
        #print("amount: "+ amount)
        currency = "THB"
        status =  body['status'] # "success" or "fail"
        transaction_state = body['transaction_state']
        text_builder = charge_id + amount + currency + status + transaction_state + settings.KBANK_SKEY
        #print(text_builder)
        text_builder_hash = hashlib.sha256(text_builder.encode('utf-8')).hexdigest()
        #print(text_builder_hash)
        checksum = body['checksum']
        #print(checksum)
        # If checksum is equal to the store information, Then update order status, amount, notify and send the email out
        if text_builder_hash == checksum:
            #print("checksum is equal")
            order.status = 'process'
            order.paid = True
            order.notify = True
            order.paid_amount = body['amount']
            #order.kbank_charge_id = charge_id
            order.save()
            order_created.delay(order_id)
            return HttpResponse(status=200)
        else :
            order.status = 'paymentfail'
            order.paid = False
            return 'nothing'
           
    
    return 'nothing'