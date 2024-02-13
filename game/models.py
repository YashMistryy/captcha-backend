from django.db import models
# from django.contrib.auth.models import User
from users.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Plan(models.Model):
    name = models.CharField(max_length=255)
    amount = models.PositiveIntegerField(null=False)
    captcha_limit = models.PositiveIntegerField(null=False)
    referral_amount = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(default=60)
    withdraw_limit = models.PositiveIntegerField(default=200)   
    def __str__(self):
        return str(self.name) + str(self.amount)
    
class PaymentTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transactionId = models.CharField(max_length=50,default='transctn_id')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    upi_id = models.CharField(max_length=50,default='upi_id',unique=False,null=True)
    date = models.DateTimeField(auto_now_add=True)
    refferal_id = models.CharField(max_length=50,default='reff_id')
    payment_screenshot = models.ImageField(upload_to='screenshots/images/',null=True,blank=True,default='default_payment_screenshot.jpg')
    SUCCESS = 'Success'
    FAILURE = 'Failure'
    PENDING = 'Pending'
    STATUS_CHOICES = [
        (SUCCESS, 'Success'),
        (FAILURE, 'Failure'),
        (PENDING, 'Pending'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

class WithdrawTransaction(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    upi_id = models.CharField(max_length=50)
    bank_id = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True)
    SUCCESS = 'Success'
    FAILURE = 'Failure'
    PENDING = 'Pending'
    STATUS_CHOICES = [
        (SUCCESS, 'Success'),
        (FAILURE, 'Failure'),
        (PENDING, 'Pending'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f"WithdrawTransaction - Amount: {self.amount}, UPI ID: {self.upi_id}, Bank ID: {self.bank_id}, Date: {self.date}"


class CaptchaPlanRecord(models.Model): # store info of user and plan -- like courseenrollment ?
    user = models.ForeignKey(User, on_delete=models.CASCADE,unique=True)
    plan = models.ForeignKey("Plan", verbose_name=(""), on_delete=models.CASCADE)
    total_captchas_filled = models.PositiveIntegerField(default=0)
    captchas_filled_today = models.PositiveIntegerField(default=0)
    is_plan_over = models.BooleanField(default=False)
    is_plan_active = models.BooleanField(default=False)
    last_captcha_fill_date = models.DateField(default=timezone.now)
    start_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
    
    # @property
    def remaining_days(self):
        """
        Calculate the number of remaining days for the plan.
        """
        if self.start_date:
            end_date = self.start_date + timezone.timedelta(days=self.plan.duration)
            remaining_days = (end_date - timezone.now()).days
            return max(0, remaining_days)  # Ensure non-negative value
        else:
            return 0  # If start_date is not set, return 0 remaining days
        
    def fill_captcha(self):
        today = timezone.now().date()
        if self.last_captcha_fill_date != today:
            # If the last captcha fill date is not today, reset the count
            self.captchas_filled_today = 0
        # Increment both the total count and the count for today
        self.total_captchas_filled += 1
        self.captchas_filled_today += 1
        self.last_captcha_fill_date = today
        self.save()

