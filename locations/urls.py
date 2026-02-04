from django.urls import path
from .views import (
    CityListAPIView,
    CityCreateAPIView,
    CityDetailAPIView,
    CityUpdateAPIView,
    CityStatusUpdateAPIView,
    CityDeleteAPIView,
    AreaListAPIView,
    AreaCreateAPIView,
    AreaDetailAPIView,
    AreaUpdateAPIView,
    AreaStatusUpdateAPIView,
    AreaDeleteAPIView,
)

urlpatterns = [
    # City URLs
    path('/city/', CityListAPIView.as_view(), name='city-list'),
    path('/city/create/', CityCreateAPIView.as_view(), name='city-create'),
    path('/city/<int:id>/', CityDetailAPIView.as_view(), name='city-detail'),
    path('/city/<int:id>/update/', CityUpdateAPIView.as_view(), name='city-update'),
    path('/city/<int:id>/change-status/', CityStatusUpdateAPIView.as_view(), name='city-status'),
    path('/city/<int:id>/delete/', CityDeleteAPIView.as_view(), name='city-delete'),
    # Area URLs
    path('/area/', AreaListAPIView.as_view(), name='area-list'),
    path('/area/create/', AreaCreateAPIView.as_view(), name='area-create'),
    path('/area/<int:id>/', AreaDetailAPIView.as_view(), name='area-detail'),
    path('/area/<int:id>/update/', AreaUpdateAPIView.as_view(), name='area-update'),
    path('/area/<int:id>/change-status/', AreaStatusUpdateAPIView.as_view(), name='area-status'),
    path('/area/<int:id>/delete/', AreaDeleteAPIView.as_view(), name='area-delete'),
]
