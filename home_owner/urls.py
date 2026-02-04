from django.urls import path
from .views import (
    HomeOwnerSignUpAPIView, VerifyEmailAPIView, VerifyPhoneAPIView, VerifyQBoxAPIView, VerifyOTPAPIView,
    HomeOwnerListAPIView, HomeOwnerStatusUpdateAPIView, HomeOwnerDeleteAPIView,
    ForgotPasswordAPIView, VerifyForgotPasswordOTPAPIView, ResetPasswordAPIView,
)
urlpatterns = [
    path('/sign_up', HomeOwnerSignUpAPIView.as_view(), name='home-owner-signup'),
    path('/send-email-otp', VerifyEmailAPIView.as_view(), name='send-email-otp'),
    path('/send-phone-otp', VerifyPhoneAPIView.as_view(), name='send-phone-otp'),
    path('/verify-otp', VerifyOTPAPIView.as_view(), name='verify-otp'),
    path('/verify-qbox', VerifyQBoxAPIView.as_view(), name='verify-qbox'),
    path('/forgot-password', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('/verify-forgot-password-otp', VerifyForgotPasswordOTPAPIView.as_view(), name='verify-forgot-password-otp'),
    path('/reset-password', ResetPasswordAPIView.as_view(), name='reset-password'),
    path('/', HomeOwnerListAPIView.as_view(), name='homeowner-list'),
    path('/<uuid:id>/status/', HomeOwnerStatusUpdateAPIView.as_view(), name='homeowner-status'),
    path('/<uuid:id>/delete/', HomeOwnerDeleteAPIView.as_view(), name='homeowner-delete'),
]