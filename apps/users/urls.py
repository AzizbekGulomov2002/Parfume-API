from django.urls import path

from .views import *

urlpatterns = [
    path('auth/reg/register/', RegisterAPIView.as_view(), name='user-register'),
    path('auth/reg/verify-otp/', VerifyOtpAPIView.as_view(), name='verify-otp'),

    path('auth/reg/login/', LoginApiView.as_view(), name='user-login'),
    # path('auth/reg/choice-otp/', OTPChoiceView.as_view(), name='choice-otp'),

    path('auth/forget/forget-password/', ForgotPasswordView.as_view(), name='forget-password'),
    path('auth/forget/reset-password/', ResetPasswordView.as_view(), name='reset-password'),

    path('auth/profile/update/', UpdateProfileAPIView.as_view(), name='update-profile'),
    path('auth/me/', MeAPIView.as_view(), name='me'),

    path('auth/reset-otp-verify/', ResendVerificationCodeAPIView.as_view(), name='reset-otp-verify'),


]
