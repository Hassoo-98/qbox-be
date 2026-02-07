from django.urls import path
from .views import (
    PackageListAPIView,
    PackageDetailAPIView,
    PackageCreateAPIView,
    PackageUpdateAPIView,
    PackageStatusUpdateAPIView,
    PackageDeleteAPIView
)
urlpatterns = [
    path('', PackageListAPIView.as_view(), name='package-list'),
    path('create', PackageCreateAPIView.as_view(), name='package-create'),
    path('<uuid:id>', PackageDetailAPIView.as_view(), name='package-detail'),
    path('<uuid:id>/update', PackageUpdateAPIView.as_view(), name='package-update'),
    path('<uuid:id>/change-status', PackageStatusUpdateAPIView.as_view(), name='package-status'),
    path('<uuid:id>/delete', PackageDeleteAPIView.as_view(), name='package-delete'),
]
