from django.urls import path
from .views import (
    StaffListAPIView,
    StaffCreateAPIView,
    StaffStatusUpdateAPIView,
    StaffUpdateAPIView,
    StaffDeleteAPIView,
    StaffDetailAPIView
)

urlpatterns = [
    path("", StaffListAPIView.as_view(), name="staff-list"),
    path("create", StaffCreateAPIView.as_view(), name="create-staff"),
    path("<uuid:id>", StaffDetailAPIView.as_view(), name="staff-detail"),
    path("<uuid:id>/update", StaffUpdateAPIView.as_view(), name="staff-update"),
    path("<uuid:id>/delete", StaffDeleteAPIView.as_view(), name="staff-delete"),
    path("<uuid:id>/change-status", StaffStatusUpdateAPIView.as_view(), name="staff-change-status"),
]
