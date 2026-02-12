from django.urls import path
from .views import (
    PackageListAPIView,
    PackageDetailAPIView,
    PackageCreateAPIView,
    PackageUpdateAPIView,
    PackageStatusUpdateAPIView,
    PackageDeleteAPIView,
    SendPackageAPIView,
    ReturnPackageAPIView,
    OutgoingPackagesAPIView,
    DeliveredPackagesAPIView,
    IncomingPackagesAPIView,
    IncomingPackageDetailAPIView,
    OutgoingPackageDetailAPIView,
    DeliveredPackageDetailAPIView,
)

# NOTE: The order of URL patterns matters!
# Specific paths like 'outgoing/', 'send/', 'return/' must come BEFORE the '<uuid:id>' pattern
# to avoid UUID matching conflicts (UUIDs contain hyphens which can match words like 'outgoing')

urlpatterns = [
    # List and Create endpoints
    path('', PackageListAPIView.as_view(), name='package-list'),
    path('create/', PackageCreateAPIView.as_view(), name='package-create'),
    
    # Send and Return package endpoints
    path('send/', SendPackageAPIView.as_view(), name='package-send'),
    path('return/', ReturnPackageAPIView.as_view(), name='package-return'),
    
    # Filtered list endpoints (MUST come before <uuid:id> pattern)
    path('outgoing/', OutgoingPackagesAPIView.as_view(), name='packages-outgoing'),
    path('delivered/', DeliveredPackagesAPIView.as_view(), name='packages-delivered'),
    path('incoming/', IncomingPackagesAPIView.as_view(), name='packages-incoming'),
    
    # Incoming package detail (MUST come before <uuid:id> pattern)
    path('incoming/<uuid:id>/', IncomingPackageDetailAPIView.as_view(), name='incoming-package-detail'),
    
    # Outgoing package detail (MUST come before <uuid:id> pattern)
    path('outgoing/<uuid:id>/', OutgoingPackageDetailAPIView.as_view(), name='outgoing-package-detail'),
    
    # Delivered package detail (MUST come before <uuid:id> pattern)
    path('delivered/<uuid:id>/', DeliveredPackageDetailAPIView.as_view(), name='delivered-package-detail'),
    
    # Individual package operations (MUST come after filtered endpoints)
    path('<uuid:id>/', PackageDetailAPIView.as_view(), name='package-detail'),
    path('<uuid:id>/update/', PackageUpdateAPIView.as_view(), name='package-update'),
    path('<uuid:id>/change-status/', PackageStatusUpdateAPIView.as_view(), name='package-status'),
    path('<uuid:id>/delete/', PackageDeleteAPIView.as_view(), name='package-delete'),
]
