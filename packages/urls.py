from django.urls import path
from .views import (
    PackageListAPIView, PackageDetailAPIView, PackageByTrackingIdAPIView,
    PackageCreateAPIView, PackageUpdateAPIView, PackageDeleteAPIView,
    PackagesByQboxIdAPIView
)

urlpatterns = [
    path('/', PackageListAPIView.as_view(), name='package-list'),
    path('/create/', PackageCreateAPIView.as_view(), name='package-create'),
    path('/<uuid:id>/', PackageDetailAPIView.as_view(), name='package-detail'),
    path('/<uuid:id>/update/', PackageUpdateAPIView.as_view(), name='package-update'),
    path('/<uuid:id>/delete/', PackageDeleteAPIView.as_view(), name='package-delete'),
    path('/by-tracking-id/<str:tracking_id>/', PackageByTrackingIdAPIView.as_view(), name='package-by-tracking-id'),
    path('/by-qbox/<uuid:qbox_uuid>/', PackagesByQboxIdAPIView.as_view(), name='packages-by-qbox'),
]
