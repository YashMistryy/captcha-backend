from django.shortcuts import render
from rest_framework import views ,permissions,response,status
from .serializers import RegisterUserSerializer
# Create your views here.
# class RegisterUser()

class RegisterUser(views.APIView):
    # permission_classes = [permissions.AllowAny]
    def post(self,request):
        reg_serializer = RegisterUserSerializer(data=request.data)
        if reg_serializer.is_valid():
            # create the user as details are provided correctly
            new_user = reg_serializer.save()
            if new_user:
                return response.Response(status=status.HTTP_201_CREATED)
        return response.Response(status=status.HTTP_400_BAD_REQUEST,data=reg_serializer.errors)