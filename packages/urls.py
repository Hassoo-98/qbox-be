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
    path('/', PackageListAPIView.as_view(), name='package-list'),
    path('/create/', PackageCreateAPIView.as_view(), name='package-create'),
    path('/<int:id>/', PackageDetailAPIView.as_view(), name='package-detail'),
    path('/<int:id>/update/', PackageUpdateAPIView.as_view(), name='package-update'),
    path('/<int:id>/change-status/', PackageStatusUpdateAPIView.as_view(), name='package-status'),
    path('/<int:id>/delete/', PackageDeleteAPIView.as_view(), name='package-delete'),
]
