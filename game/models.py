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
    def __str__(self):
        return self.name
    
class PaymentTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    SUCCESS = 'Success'
    FAILURE = 'Failure'
    PENDING = 'Pending'
    STATUS_CHOICES = [
        (SUCCESS, 'Success'),
        (FAILURE, 'Failure'),
        (PENDING, 'Pending'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

class CaptchaPlanRecord(models.Model): # store info of user and plan -- like courseenrollment ?
    user = models.ForeignKey(User, on_delete=models.CASCADE,unique=True)
    plan = models.ForeignKey("Plan", verbose_name=(""), on_delete=models.CASCADE)
    total_captchas_filled = models.PositiveIntegerField(default=0)
    captchas_filled_today = models.PositiveIntegerField(default=0)
    is_plan_over = models.BooleanField(default=False)
    is_plan_active = models.BooleanField(default=False)
    last_captcha_fill_date = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
    
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

