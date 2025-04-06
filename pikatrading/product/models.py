from django.db import models
from django.core.files import File
from io import BytesIO
from PIL import Image
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    background = models.ImageField(upload_to='uploads/', blank=True, null=True, default='default.jpg')
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='uploads/', blank=True, null=True)

    class Meta:
        ordering = ('name',)
    
    def __str__(self):
        return self.name
    
    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()
                print(self.thumbnail.url)
                return self.thumbnail.url
            else:
                return 'https://s3.amazonaws.com/s3.myslabs.com/media/68f5bc6b-1c05-4b5c-8206-c85a007bc979/2023/08/17/YNKECJF_1692281346_1.png'
    
    def make_thumbnail(self, image, size=(300, 300)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    sku = models.CharField(max_length=100, unique=True)  # SKU field
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()
    vendor_class_C_price = models.FloatField(blank=True, null=True)# price for vendor C
    vendor_class_B_price = models.FloatField(blank=True, null=True)# price for vendor B
    vendor_class_A_price = models.FloatField(blank=True, null=True)# price for vendor A
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='uploads/', blank=True, null=True)
    quantity = models.IntegerField()
    vendor_class_C_min_quantity = models.IntegerField(blank=True, null=True)
    vendor_class_B_min_quantity = models.IntegerField(blank=True, null=True)
    vendor_class_A_min_quantity = models.IntegerField(blank=True, null=True)
    stock = models.IntegerField(default=20, null=True)
    weight = models.FloatField(help_text="Weight in grams")
    unit = models.CharField(max_length=255)
    #min_quantity = models.IntegerField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created_at',)
    
    def save(self, *args, **kwargs): # automatic assign default price and quantity for vendor if it did not set up during product creation
        if self.vendor_class_C_price is None:
            self.vendor_class_C_price = self.price
        if self.vendor_class_B_price is None:
            self.vendor_class_B_price = self.price
        if self.vendor_class_A_price is None:
            self.vendor_class_A_price = self.price
        
        if self.vendor_class_C_min_quantity is None:
            self.vendor_class_C_min_quantity = 1
        if self.vendor_class_B_min_quantity is None:
            self.vendor_class_B_min_quantity = 1
        if self.vendor_class_A_min_quantity is None:
            self.vendor_class_A_min_quantity = 1

        super(Product, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    def get_display_price(self,user_id):
        if user_id is None:
            return self.price
        else:
            user = User.objects.get(pk=user_id)

            if  user.profile.user_type == 'Vendor_Class_C':
                return self.vendor_class_C_price
            elif user.profile.user_type == 'Vendor_Class_B':
                return self.vendor_class_B_price
            elif user.profile.user_type == 'Vendor_Class_A':
                return self.vendor_class_A_price
            else :
                return self.price

        return self.price

    def get_min_quantity(self,user_id):
        if user_id is None:
            return self.quantity
        else:
            user = User.objects.get(pk=user_id)

            if  user.profile.user_type == 'Vendor_Class_C':
                return self.vendor_class_C_min_quantity
            elif user.profile.user_type == 'Vendor_Class_B':
                return self.vendor_class_B_min_quantity
            elif user.profile.user_type == 'Vendor_Class_A':
                return self.vendor_class_A_min_quantity
            else :
                return self.quantity

        return self.quantity
   
    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()

                return self.thumbnail.url
            else:
                return 'https://s3.amazonaws.com/s3.myslabs.com/media/68f5bc6b-1c05-4b5c-8206-c85a007bc979/2023/08/17/YNKECJF_1692281346_1.png'
    
    def make_thumbnail(self, image, size=(300, 300)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail
