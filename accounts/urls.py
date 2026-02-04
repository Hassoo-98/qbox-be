from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    RegisterView,
    LoginView,
    UserProfileView,
    ChangePasswordView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    UserViewSet,
    VerifyEmailView,
    OTPVerificationView,
)

urlpatterns = [
    path('/register/', RegisterView.as_view(), name='register'),
    path('/login/', LoginView.as_view(), name='login'),
    path('/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('/profile/', UserProfileView.as_view(), name='profile'),
    path('/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('/password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('/email-verify/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='email_verify'),
    path('/otp-verify/', OTPVerificationView.as_view(), name='otp_verify'),
]
