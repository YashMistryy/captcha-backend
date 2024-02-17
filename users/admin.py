
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # Customize the admin interface if needed
    list_display = ('id','username', 'current_balance', 'mobile_number', 'first_name', 'member_id','referral_id', 'is_staff')
    fieldsets = (("Our User",{'fields': ('first_name','username','mobile_number', 'current_balance', 'is_staff')}),)
admin.site.register(User, CustomUserAdmin)

