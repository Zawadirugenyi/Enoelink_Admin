from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from users.models import User
from users.serializers import RegistrationSerializer, LoginUserSerializer

from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from users.serializers import RegistrationSerializer, LoginUserSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny





class SignInUserView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']
            email = serializer.validated_data['email']
            phone_number = serializer.validated_data['phone_number']
            password = serializer.validated_data['password']

            # Create user
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
            )
            user.set_password(password)
            user.save()

            # Create token
            token, created = Token.objects.get_or_create(user=user)

            # Try to send welcome email, but don't block signup
            try:
                send_mail(
                    'Welcome to EneoLink!',
                    f'Hi {first_name},\n\n'
                    'Thank you for signing up with EneoLink! We are happy to have you here.\n\n'
                    'Best regards,\nEneoLink Team',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Warning: Failed to send welcome email to {email}: {e}")
                # Do not return; signup succeeds even if email fails

            # Always return success
            response_content = {
                'status': True,
                'message': 'User registered successfully!',
                'token': token.key,
            }
            return Response(response_content, status=status.HTTP_201_CREATED)

        # Invalid serializer
        return Response({
            'status': False,
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)



class LoginUserView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginUserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = User.objects.get(email=email)

            if not user.check_password(password):
                return Response({'status': False, 'message': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)

            token, created = Token.objects.get_or_create(user=user)

            response_content = {
                'status': True,
                'message': 'User logged in successfully.',
                'token': token.key,
            }

            return Response(response_content, status=status.HTTP_200_OK)

        response_content = {
            'status': False,
            'message': serializer.errors,
        }

        return Response(response_content, status=status.HTTP_400_BAD_REQUEST)

class LogoutUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user

        try:
            token = Token.objects.get(user=user)
            token.delete()
            # Replace 'username' with the appropriate attribute, e.g., 'email' if 'username' does not exist
            print(f'Token for user {user.email} successfully deleted.')
        except Token.DoesNotExist:
            return Response({'status': False, 'message': 'No active session found.'}, status=status.HTTP_400_BAD_REQUEST)

        response_content = {
            'status': True,
            'message': 'User logged out successfully.'
        }

        return Response(response_content, status=status.HTTP_200_OK)


 # users/views.py
    # users/views.py
from django.contrib.auth import get_user_model
User = get_user_model()

# users/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
import json

User = get_user_model()

@csrf_exempt
def check_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            first_name = data.get('first_name')
            email = data.get('email')

            user_exists = User.objects.filter(first_name=first_name, email=email).exists()
            return JsonResponse({'exists': user_exists})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Password must be at least 8 characters long, include at least one letter, one number, and one special character.'}, status=400)

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.utils.crypto import get_random_string
from users.models import User

class SendBypassCodeView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({'status': False, 'message': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'status': False, 'message': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a random bypass code
        bypass_code = get_random_string(6, allowed_chars='1234567890')

        # You can save the bypass code to the user model or send it directly.
        # For simplicity, we are only sending the email here.
        
        try:
            send_mail(
                'Your Bypass Code',
                f'Hello {user.first_name},\n\nYour bypass code is: {bypass_code}\n\nBest regards,\nEneoLink Team',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        except BadHeaderError:
            return Response({'status': False, 'message': 'Invalid header found in email.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': False, 'message': f'Failed to send bypass code email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'status': True, 'message': 'Bypass code sent successfully'}, status=status.HTTP_200_OK)
