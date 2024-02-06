from django.contrib import admin
from game.models import Plan,CaptchaPlanRecord,PaymentTransaction , WithdrawTransaction



# Register your models here.
admin.site.register(Plan)
admin.site.register(CaptchaPlanRecord)
admin.site.register(PaymentTransaction)
admin.site.register(WithdrawTransaction)
