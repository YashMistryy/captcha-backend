from django.contrib import admin
from game.models import Plan,CaptchaPlanRecord,PaymentTransaction , WithdrawTransaction

class GameAdmin(admin.ModelAdmin):
    list_display = ('id','user','plan')
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id','user','amount','date' ,'refferal_id','status')
class WithdrawAdmin(admin.ModelAdmin):
    list_display = ('id','user','amount','date','upi_id','status')


# Register your models here.
admin.site.register(Plan)
admin.site.register(CaptchaPlanRecord,GameAdmin)
admin.site.register(PaymentTransaction,PaymentAdmin)
admin.site.register(WithdrawTransaction,WithdrawAdmin)
