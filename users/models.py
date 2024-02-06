# creating our custom user model here
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
import uuid

def generate_unique_id():
    return str(uuid.uuid4())[:7]
class UserManager(BaseUserManager):
    def create_user(self, mobile_number, password=None, **extra_fields):
        if not mobile_number:
            raise ValueError('The Mobile Number field must be set')

        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(mobile_number, password, **extra_fields)

class User(AbstractUser):
    # Existing fields
    age = models.PositiveIntegerField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    # New fields
    member_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
    current_balance = models.PositiveIntegerField(default=0, blank=True)
    times_reffered = models.PositiveIntegerField(default=0)
    current_plan = models.ForeignKey("game.Plan", verbose_name=(""), on_delete=models.CASCADE,null=True)
    referral_id = models.CharField(max_length=7, default=generate_unique_id, editable=False)
    mobile_number = models.CharField(null=False,unique=True,max_length=10,validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Must be exactly 10 digits.',
                code='invalid_10_digits'
            )
        ])
    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['password']
    objects = UserManager()
    def save(self, *args, **kwargs):
        # Generate member_id when the user is created
        if not self.member_id:
            # Save the instance to get the id assigned by the database
            super().save(*args, **kwargs)
            self.member_id = "GY012" + str(self.id + 24)  # just a fancy unique id
            self.username = self.mobile_number

            # Save again with the member_id and updated username
            super().save(*args, **kwargs)
        else:
            # If member_id is already generated, only save once
            super().save(*args, **kwargs)


  # Take the first 7 characters of the UUID
