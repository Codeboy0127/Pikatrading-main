from itertools import product
from django.contrib.auth.models import User
from django.db import models


from product.models import Product

class Order(models.Model):
    ORDERED = 'ordered' # This value will store in database
    PROCESS = 'process'
    SHIPPED = 'shipped' # This value will store in database
    PAYMENTFAIL = 'paymentfail'

    STATUS_CHOICES = (
        (ORDERED, 'Ordered'),# the last parameter will be shown in admin interface
        (PROCESS, 'Processing'),
        (SHIPPED, 'Shipped'),# the last parameter will be shown in admin interface
        (PAYMENTFAIL, 'Payment Fail')
    )

    user = models.ForeignKey(User, related_name='orders', blank=True, null=True, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=255, blank=True, null=True)
    ## SHIPPING INFORMATION ##
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    ## BILLING INFORMATION ##
    first_name_billing = models.CharField(max_length=255)
    last_name_billing = models.CharField(max_length=255)
    address_billing = models.CharField(max_length=255)
    zipcode_billing = models.CharField(max_length=255)
    place_billing = models.CharField(max_length=255)


    ## PERSONEL INFORMATION ##    
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)

    product_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Total cost exclude shipping cost")
    product_amount_bf_tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Total cost exclude shipping cost & before tax")
    vat = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="VAT % of product amount")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    paid = models.BooleanField(default=False)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    ## Kbank information for payment processs ##
    notify = models.BooleanField(default=False)
    kbank_order_id = models.CharField(max_length=255, blank=True, null=True)
    kbank_charge_id = models.CharField(max_length=255, blank=True, null=True)
    kbank_token_id = models.CharField(max_length=255, blank=True, null=True)
    payment_method = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ORDERED)

    # Shipping
    shipping_method = models.CharField(max_length=255, blank=True, null=True)
    tracking_number = models.CharField(max_length=255, blank=True, null=True)
    shipping_url_printing = models.URLField(blank=True, null=True)

    # Invoice
    invoice = models.FileField(upload_to='invoices/', blank=True, null=True)  # File upload field

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete
    =models.CASCADE)
    product = models.ForeignKey(Product, related_name='items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

class ShippingRate(models.Model):
    
    min_weight = models.DecimalField(max_digits=10, decimal_places=2)  # grams
    max_weight = models.DecimalField(max_digits=10, decimal_places=2)  # grams
    rate = models.DecimalField(max_digits=10, decimal_places=2)  # price

    def __str__(self):
        return f"{self.min_weight}-{self.max_weight} grams - ฿{self.rate}"