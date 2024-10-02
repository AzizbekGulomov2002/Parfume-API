import uuid
from django.contrib.auth.backends import ModelBackend
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

from apps.users.models import UserImage
from .models import CustomUser as User
from .serializers import *
import random
from django.contrib.auth import authenticate, login
from rest_framework.authentication import TokenAuthentication



class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Always return messages in English
        lang = 'en'

        serializer = UserRegisterSerializer(data=request.data)

        # Validate request data
        if not serializer.is_valid():
            return Response({
                "message": "The provided data is invalid.",
                "errors": serializer.errors  # Include specific validation errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if email or phone already exists
        email = request.data.get('email')
        phone = request.data.get('phone')
        error_messages = {}

        # Validate email uniqueness
        if CustomUser.objects.filter(email=email).exists():
            error_messages['email'] = "This email is already in use."

        # Validate phone uniqueness
        if CustomUser.objects.filter(phone=phone).exists():
            error_messages['phone'] = "This phone number is already in use."

        # If there are any errors, return them
        if error_messages:
            return Response({
                "message": "The following errors occurred.",
                "errors": error_messages
            }, status=status.HTTP_400_BAD_REQUEST)

        # Save user
        user = serializer.save()

        # Generate a 5-digit random verification code
        verification_code = random.randint(10000, 99999)
        user.verification_code = verification_code  # Store the verification code
        user.verification_code_time = timezone.now()  # Set the time for the verification code
        user.save()

        # Send verification code via email
        self.send_verification_email(user.email, user.verification_code)

        return Response({
            "message": "A 5-digit activation code has been sent to your email. Please enter the code within 4 minutes.",
            "user_id": user.id,
            "email": email
        }, status=status.HTTP_201_CREATED)

    def send_verification_email(self, email, verification_code):
        """Send the verification code to the user's email with HTML styling."""
        subject = "Your Activation Code"
        
        # Use the absolute URL for your logo
        logo_url = 'https://example.com/static/logo/industrify-logo.jpg'  # Update this URL

        # Create the HTML message
        message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your Activation Code</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f6f6f6;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: auto;
                    background: blue;  /* Blue background */
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    position: relative;
                    background-image: url('{logo_url}');  /* Use absolute URL for logo */
                    background-size: contain; 
                    background-repeat: no-repeat; 
                    background-position: center; 
                }}
                h1, p {{
                    color: white; /* Set all text color to white */
                    font-weight: bold; /* Set text to bold */
                }}
                .code {{
                    display: inline-block;
                    padding: 10px 15px;
                    background-color: #007bff; /* Blue background for code */
                    color: white; /* Keep the code text white */
                    border-radius: 5px;
                    font-size: 20px;
                    font-weight: bold;
                }}
                footer {{
                    margin-top: 20px;
                    font-size: 12px;
                    color: #ddd; /* Light gray for footer text */
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Your Activation Code</h1>
                <p>Thank you for registering with us. Please use the following activation code to complete your registration:</p>
                <p class="code">{verification_code}</p>
                <p>This code is valid for 4 minutes. If you did not request this code, please ignore this email.</p>
                <footer>
                    <p>&copy; {timezone.now().year} Your Company Name. All rights reserved.</p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        # Send the email
        send_mail(
            subject=subject,
            message="",  # Use an empty message since we're sending HTML
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
            html_message=message  # Specify the HTML message
        )

class VerifyOtpAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        verification_code = request.data.get('verification_code')

        try:
            user_instance = CustomUser.objects.get(id=user_id)

            # Check if the verification code has expired (4 minutes)
            expiration_time = user_instance.verification_code_time + timedelta(minutes=4)
            if timezone.now() > expiration_time:
                user_instance.is_active = False
                user_instance.verification_code = None  # Clear the verification code
                user_instance.save()

                return Response({
                    "error": "The verification code has expired. Please request a new code."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if the verification code matches
            if user_instance.verification_code != verification_code:
                return Response({
                    "error": "Incorrect verification code."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Activate the user
            user_instance.is_active = True
            user_instance.verification_code = None  # Clear the verification code
            user_instance.save()

            return Response({
                "message": "Your email has been verified. You can now log in."
            }, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({
                "error": "User not found."
            }, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationCodeAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')

        try:
            user_instance = CustomUser.objects.get(id=user_id)

            # Generate a new 5-digit verification code
            new_verification_code = uuid.uuid4().int % 100000  # Generate a 5-digit code
            user_instance.verification_code = new_verification_code
            user_instance.verification_code_time = timezone.now()  # Set the time for the verification code
            user_instance.save()

            # Send the new verification code via email
            send_mail(
                subject="Your Verification Code",
                message=f"Your verification code is: {new_verification_code}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user_instance.email]
            )

            return Response({
                "message": "A new verification code has been sent to your email."
            }, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({
                "error": "User not found."
            }, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username_or_email = request.data.get('username_or_email')

        # Ensure the required field is provided
        if not username_or_email:
            return Response({
                "error": "Email must be provided."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Try to find the user by email or username
        try:
            user = CustomUser.objects.get(email=username_or_email)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(phone=username_or_email)
            except CustomUser.DoesNotExist:
                return Response({
                    "error": "No user found with this username or email."
                }, status=status.HTTP_400_BAD_REQUEST)

        # Generate and send a verification code
        verification_code = random.randint(10000, 99999)
        user.verification_code = verification_code
        user.verification_code_time = timezone.now()
        user.save()

        # Send the verification code via email
        send_mail(
            subject="Password Reset Code",
            message=f"Your password reset code is: {verification_code}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email]
        )

        return Response({
            "message": "A confirmation code has been sent to the email."
        }, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username_or_email = request.data.get('username_or_email')
        verification_code = request.data.get('verification_code')
        new_password = request.data.get('new_password')

        # Ensure all required fields are provided
        if not username_or_email or not verification_code or not new_password:
            return Response({
                "error": "Username or email, confirmation code, and new password must be provided."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Try to find the user by email or username
        try:
            user = User.objects.get(email=username_or_email)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=username_or_email)
            except User.DoesNotExist:
                return Response({
                    "error": "No user found with this username or email."
                }, status=status.HTTP_400_BAD_REQUEST)

        # Check if the verification code is correct
        if user.verification_code != int(verification_code):
            return Response({
                "error": "The code is incorrect."
            }, status=status.HTTP_400_BAD_REQUEST)

        # If verification code is correct, reset the password
        user.set_password(new_password)  # Set the new password
        user.verification_code = None  # Clear the verification code after use
        user.save()  # Save changes to the user

        return Response({
            "message": "Password has been successfully changed."
        }, status=status.HTTP_200_OK)

class LoginApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_or_email = request.data.get('phone_or_email')
        password = request.data.get('password')

        # Check for empty fields
        if not phone_or_email:
            return Response({
                "error": "Username or email must be provided."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not password:
            return Response({
                "error": "Password must be provided."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Try to authenticate the user using the custom backend
        user_auth = authenticate(request, username=phone_or_email, password=password)

        if user_auth is None:
            return Response({
                "error": "Incorrect password."
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the user's account is active
        if not user_auth.is_active:
            return Response({
                "error": "User is not verified."
            }, status=status.HTTP_403_FORBIDDEN)

        # Get or create the token for the authenticated user
        token, created = Token.objects.get_or_create(user=user_auth)

        # Return a success response with the token
        return Response({
            "success": "Successfully logged in.",
            "token": token.key
        }, status=status.HTTP_200_OK)

class UpdateProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Use IsAuthenticated for security

    def put(self, request):
        user = request.user
        
        # Allow only full_name to be updated
        serializer = UserProfileSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            # Update the user's full_name if provided
            full_name = serializer.validated_data.get('full_name', user.full_name)

            # Save the user profile if full_name is provided
            user.full_name = full_name
            user.save()

 

            return Response({
                "message": "Profile updated successfully.",  # Return a simple English message
            }, status=status.HTTP_200_OK)

        return Response({
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    


User = get_user_model()  # Get the custom user model

class MeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can access this view
    authentication_classes = [TokenAuthentication]  # Use token authentication

    def get(self, request):
        user = request.user  # Get the authenticated user
        
        # Retrieve the first user's image URL, if it exists
        user_image = UserImage.objects.filter(user=user).first()  # Get the first image or None
        image_url = user_image.image.url if user_image else None  # Get the image URL or None if no image exists
        
        user_data = {
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "image": image_url  # Include the image URL (or None) directly
        }
        
        return Response(user_data, status=status.HTTP_200_OK)


class CustomAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(email=username) or UserModel.objects.get(phone=username)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

