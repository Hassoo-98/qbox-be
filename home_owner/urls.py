from django.urls import path
from .views import (
    HomeOwnerListAPIView,
    HomeOwnerCreateAPIView,
    HomeOwnerStatusUpdateAPIView,
    HomeOwnerUpdateAPIView,
    HomeOwnerDeleteAPIView,
    HomeOwnerDetailAPIView,
    HomeOwnerLoginView,
    HomeOwnerResetPasswordView,
)
urlpatterns = [
    path("/login", HomeOwnerLoginView.as_view(), name="homeowner-login"),
    path("/reset-password", HomeOwnerResetPasswordView.as_view(), name="homeowner-reset-password"),
    path("/", HomeOwnerListAPIView.as_view(), name="homeowner-list"),
    path("/create", HomeOwnerCreateAPIView.as_view(), name="homeowner-create"),
    path("/<uuid:id>", HomeOwnerDetailAPIView.as_view(), name="homeowner-detail"),
    path("/<uuid:id>/update", HomeOwnerUpdateAPIView.as_view(), name="homeowner-update"),
    path("/<uuid:id>/status", HomeOwnerStatusUpdateAPIView.as_view(), name="homeowner-status"),
    path("/<uuid:id>/delete", HomeOwnerDeleteAPIView.as_view(), name="homeowner-delete"),
]
