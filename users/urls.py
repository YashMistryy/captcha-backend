from django.urls import path , include
from .views import *
urlpatterns=[
    path("register/",RegisterUser.as_view(),name='register_user')
]