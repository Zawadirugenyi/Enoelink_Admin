from .models import User
from rest_framework import serializers
from rest_framework import status

import re 

def password_validator(password):
    if re.findall('[a-z]', password):
        if re.findall('[A-Z]', password):
            if re.findall('[0-9]', password):
                if re.findall("[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]", password):
                    if len(password) > 7:
                        return True
    return False

class RegistrationSerializer(serializers.Serializer):
    
    first_name = serializers.CharField(error_messages={'message': 'first name Required.'})
    last_name = serializers.CharField(error_messages={'message': 'last name Required.'})
    email = serializers.EmailField(error_messages={'message': 'email Required.'})
    phone_number = serializers.CharField(error_messages={'message': 'phone number Required.'})
    password = serializers.CharField(error_messages={'message': 'password Required.'})

    def validate(self, data):
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone_number = data.get('phone_number')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            user = None


        
        try:
            user_phone_no = User.objects.get(phone_number=phone_number)
        except:
            user_phone_no = None


        if user:
            raise serializers.ValidationError('User with given email already exists.')


        if user_phone_no:
            raise serializers.ValidationError('Phone Number already belongs to an account.')

            
        if not password_validator(password):
            raise serializers.ValidationError('Password must contain 1 number, 1 upper-case and lower-case letter and a special character.')

        if password == email:
            raise serializers.ValidationError('Password cannot be your Email.')


        return data



class LoginUserSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            user = None

        if not user:
            raise serializers.ValidationError({'message': 'Account with email does not exists.'}, code=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            raise serializers.ValidationError({'message': 'Password is incorrect.'}, code=status.HTTP_401_UNAUTHORIZED)
                
        if not user.is_active:
            raise serializers.ValidationError('User is not active.')

        return data


        