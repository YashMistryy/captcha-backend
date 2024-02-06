# path for most of game routes
from django.urls import path
from .views import *
urlpatterns = [
    path("greet",greet),
    path("check-if-enroll",check_if_enrolled),
    path("user-details",get_user_details),
    path("plan-details",get_plan_details ,name="get-plan-details"),
    path("select-plan/",select_plan,name="select-plan"),
    path("submit-captcha/",submit_captcha,name='submit-captcha'),
    path("withdraw-amount/",withdraw_amount),
    path("add-funds/",add_amount),

]
