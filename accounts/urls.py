from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import (
    RegisterView,
    LoginView,
    VerifyEmailSendOTPView,
    VerifyEmailVerifyOTPView,
    Forget_PasswordView,          
    ResetPasswordConfirmView,   
)

urlpatterns = [
    path('/register/', RegisterView.as_view(), name='register'),
    path('/login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('email-verify/send-otp/', VerifyEmailSendOTPView.as_view(), name='email-verify-send-otp'),
    path('email-verify/verify-otp/', VerifyEmailVerifyOTPView.as_view(), name='email-verify-verify-otp'),
    path('password-reset/send-otp/', Forget_PasswordView.as_view(), name='password-reset-send-otp'),
    path('password-reset/confirm/', ResetPasswordConfirmView.as_view(), name='password-reset-confirm'),
]