from django.urls import path
from .views import (
    DriverListAPIView,
    DriverCreateAPIView,
    DriverUpdateAPIView,
    DriverStatusUpdateAPIView,
    DriverDeleteAPIView,
    DriverDetailAPIView,

)
urlpatterns=[
    path("",DriverListAPIView.as_view(),name="driver-list"),
    path("create",DriverCreateAPIView.as_view(),name="driver-create"),
    path("<str:id>/update",DriverUpdateAPIView.as_view(),name="driver-update"),
    path("<str:id>/delete",DriverDeleteAPIView.as_view(),name="driver-delete"),
    path("<str:id>/change-status",DriverStatusUpdateAPIView.as_view(),name="driver-change-status"),
   path("<str:id>",DriverDetailAPIView.as_view(),name="driver-list-single")
]