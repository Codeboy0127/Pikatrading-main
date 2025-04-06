from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from .models import Profile
from django.contrib.auth.models import User



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type']
    raw_id_fields = ['user']

class ProfileAdmin_Inline(admin.StackedInline):
    model = Profile
    list_display = ['user', 'user_type']
    raw_id_fields = ['user']


class UserAdmin(AuthUserAdmin):
    inlines = [ProfileAdmin_Inline]

# unregister old user admin
admin.site.unregister(User)
# register new user admin
admin.site.register(User, UserAdmin)



