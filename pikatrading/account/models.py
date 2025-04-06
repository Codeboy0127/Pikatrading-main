from django.db import models
from django.contrib.auth.models import User
class Profile(models.Model):

    NORMAL= 'normal' # This value will store in database
    VENDOR_C = 'Vendor_Class_C'
    VENDOR_B = 'Vendor_Class_B' # This value will store in database
    VENDOR_A = 'Vendor_Class_A'

    USER_TYPE_ENUM = (
        (NORMAL, 'Normal'),# the last parameter will be shown in admin interface
        (VENDOR_C, 'Vendor Class C'),
        (VENDOR_B, 'Vendor Class B'),# the last parameter will be shown in admin interface
        (VENDOR_A, 'Vendor Class A')
    )

    user = models.OneToOneField(User, related_name='profile',on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/',blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_ENUM, default=NORMAL)
    def __str__(self):
        return f'Profile of {self.user.username}'
