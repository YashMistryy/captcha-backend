# all the user related serializers are here
from rest_framework import serializers
from users.models import User
class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['mobile_number','password', 'first_name', 'last_name', 'email']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            mobile_number=validated_data['mobile_number'],
            password=validated_data['password'],
            username = validated_data['mobile_number'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
        )
        return user
    
    