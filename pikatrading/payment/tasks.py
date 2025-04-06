from celery import shared_task
from django.conf import settings
import requests
from django.core.mail import send_mail
from order.models import Order
import time
import datetime
import json
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.files import File
from io import BytesIO
import weasyprint
from playwright.sync_api import sync_playwright
import os


## KBANK INFORMATION TO MAKE REQUEST ##

url_inquire_qr_transaction = settings.KANK_INQUIRE_QR_TRANSACTION
url_inquire_cd_transaction = settings.KANK_INQUIRE_CD_TRANSACTION

header = {
            'content-type': 'application/json',
            'x-api-key': settings.KBANK_SKEY
        }
## END KBANK INFOMRATION TO MAKE REQUEST ##

## Function to send lime MESSAGE API ##
def send_line_push_message(message):
    """Sends a push message to a LINE user without using line-bot-sdk."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.LINE_ACCESS_TOKEN}"
    }

    payload = {
        "to": settings.LINE_SENT_TO_USER_ID,
        "messages": [{"type": "text", "text": message}]
    }

    response = requests.post(settings.LINE_PUSH_URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return JsonResponse({"message": "Push message sent successfully!"}, status=200)
    else:
        return JsonResponse({"error": response.text}, status=response.status_code)

def send_html_email(subject, order, is_staff):
    subject = subject
    from_email = "customersupport@pikatrading.com"

    if is_staff: # send email to staff
        recipient_list = ["raud.boss@gmail.com"]
    else:
        recipient_list = [order.email]

    # Load the HTML template
    html_content = render_to_string("order/email_order_complete.html", {"order": order, "is_staff": is_staff})
    text_content = strip_tags(html_content)  # Fallback for email clients that don't support HTML

    msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    msg.attach_alternative(html_content, "text/html")  # Attach HTML version

    # Generate PDF
    
        #html = render_to_string('order/invoice_order.html', {'order': "Order"})
        #out = BytesIO()
        #weasyprint.HTML(string=html).write_pdf(out)
    # attach PDF file
        #msg.attach(f'INV-PKXXXX.pdf',out.getvalue(),'application/pdf')
    msg.send()



@shared_task
def order_created(order_id):
    order = Order.objects.get(id = order_id)

    # Generate Shipping Label only thailand post
    if order.shipping_method == "thailandpost":
        get_shipping_label(order)



    # SEND EMAIL TO STAFF AND CUSTOMER

    # 1. Send mail to Staff
    send_html_email(f'Pika Trading Order Confirmation #{order.order_id}' , order, True)

    # 2. Send mail to Customer
    send_html_email(f'Pika Trading Order Confirmation #{order.order_id}' , order, False)

    
    # LINE MESSAGE SEND INFORMATION #

    ### LINE NOTIFICATION ORDER TEMPLATE###
    
    # 1. Header
    MESSAGE_TEMPLATE = f"""NEW ORDER: ID = {order.order_id} \nDate: {order.created_at.date()} \n ------------------------------ \n """

    # 2. order item
    
    # Access related order items
    order_items = order.items.all()
    no_item = 1
    for item in order_items:
        total_price = item.product.get_display_price(order.user.id) * item.quantity
        MESSAGE_TEMPLATE += f"""{no_item}. {item.product.name}[{item.product.sku}]:  {item.product.get_display_price(order.user.id)} บาท x {item.quantity} = {total_price} บาท\n """
        no_item += 1
    
    # 3. Customer Detail
    MESSAGE_TEMPLATE += f"""\nShipping Cost: {order.shipping_cost } บาท\nTotal*: {order.total_amount} บาท \n ------------------------------
    Customer Detail \n ------------------------------ \n
    Name: {order.first_name} {order.last_name}\n
    Address: {order.address}\n
    City/Place: {order.place}\n
    Zipcode: {order.zipcode}\n
    Email: {order.email}\n
    Phone: {order.phone}\n
    Shipping Method: {order.shipping_method}\n
    Shipping Label: {order.shipping_url_printing}\n"""
    

    send_line_push_message(MESSAGE_TEMPLATE)
    return 200

@shared_task
def qr_transaction_inquiry(order_id):
    order = Order.objects.get(id = order_id)
    # This case for we've got web hook already.
    if order.notify == True:
        return 'do nothing'
    url = ''
    # This case for we did not recieve webhook yet.
    if order.payment_method == 'qr' or order.payment_method == 'wechat':
        url = url_inquire_qr_transaction
    
    r = requests.get(url+'/'+order.kbank_order_id, headers=header)
    response_data = r.json()

    if response_data['status'] == 'success' and response_data['transaction_state'] == 'Authorized':
        order.status = 'process'
        order.paid = True
        order.paid_amount = response_data['amount']
        order.kbank_charge_id = response_data['id']
        order.save()
        order_created.delay(order_id)
    else:
        order.status = 'paymentfail'
        order.save()

    print(r.text)
    print('This is test time krub')
    print(datetime.datetime.now().time())
    return 'Sent inquiry to kbank for qr status'

@shared_task
def cd_transaction_inquiry(order_id):
    order = Order.objects.get(id = order_id)
    # This case for we've got web hook already.
    if order.notify == True:
        return 'do nothing'
    url = ''
    # This case for we did not recieve webhook yet.
    if order.payment_method == 'creditcard' or order.payment_method == 'creditcard-jut' or order.payment_method == 'alipay' :
        url = url_inquire_cd_transaction
    
    r = requests.get(url+'/'+order.kbank_charge_id, headers=header)
    response_data = r.json()

    if response_data['status'] == 'success' and response_data['transaction_state'] == 'Authorized':
        order.status = 'process'
        order.paid = True
        order.paid_amount = response_data['amount']
        #order.kbank_charge_id = response_data['id']
        order.save()
        order_created.delay(order_id)
    else:
        order.status = 'paymentfail'
        order.save()

    print(r.text)
    print('This is test time krub')
    print(datetime.datetime.now().time())
    return 'Sent inquiry to kbank for credit card status'


def get_shipping_label(order):
    
    pdf_url = generate_shipping_label(order)

    if pdf_url != None:

        order.shipping_url_printing = pdf_url
        order.save()
    else:
        return 'Shipping generator fail'


def generate_shipping_label(order):

    first_name = order.first_name
    last_name = order.last_name
    address = order.address
    zipcode = order.zipcode
    place = order.place
    phone = order.phone
    
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless= True)  # Set headless=True for production
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to the website
        page.goto('https://thailandpost-oa.com/')

        try:
            # Wait for the form to be visible
            page.wait_for_selector('form', timeout=10000)
            
            # Fill in the form fields
            # Note: Replace these selectors and values with the actual ones from the website
            # These are example selectors - you'll need to update them based on the actual form
            page.fill('[name="tid"]', 'raud_boss@hotmail.com')
            page.fill('[name="tpasswd"]', 'themafia')
            page.click('button[type="submit"]')
            print('after submit line')

            page.wait_for_selector('form', timeout=10000)
            page.fill('input[placeholder="ชื่อ นามสกุล"]', first_name + ' ' + last_name)
            page.fill('textarea[placeholder="ที่อยู่จัดส่ง"]', address + ' ' + place + ' ' + zipcode)
            page.fill('input[placeholder="เบอร์โทรศัพท์ติดต่อ"]', phone)
            time.sleep(2)
            page.click('.btn-reciever-confirm')
            print('after submit form')
            time.sleep(2)
            page.click('input[type="radio"][value="10x10"]')
            page.click('.swal2-confirm')
            print('after select paper type')
            page.locator('h2#swal2-title:text("สร้างใบจ่าหน้าสำเร็จ")').wait_for()
            

           
            
            with page.expect_download() as download_info:
                page.get_by_text("ดาวน์โหลด").click()
            # Wait for the download event
            download = download_info.value

            # Get the URL of the downloaded PDF
            pdf_url = download.url
            print(f"PDF URL: {pdf_url}")
            # Get the originating page URL
            #originating_page_url = download.page.url
            #print(f"Originating Page URL: {originating_page_url}")
                    
            #page.get_by_text("ดาวน์โหลด").click() 
            
            # Start waiting for the download
            
            print("Form filled successfully!")
            return pdf_url
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        finally:
            # Close the browser
            browser.close()





