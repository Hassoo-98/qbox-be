from django.urls import path
from .views import (
    HomeOwnerListAPIView,
    HomeOwnerCreateAPIView,
    HomeOwnerStatusUpdateAPIView,
    HomeOwnerUpdateAPIView,
    HomeOwnerDeleteAPIView,
    HomeOwnerDetailAPIView,
)

urlpatterns = [
    path("/", HomeOwnerListAPIView.as_view(), name="homeowner-list"),
    path("/create", HomeOwnerCreateAPIView.as_view(), name="homeowner-create"),
    path("/<int:id>", HomeOwnerDetailAPIView.as_view(), name="homeowner-detail"),
    path("/<int:id>/update", HomeOwnerUpdateAPIView.as_view(), name="homeowner-update"),
    path("/<int:id>/status/", HomeOwnerStatusUpdateAPIView.as_view(), name="homeowner-status"),
    path("/<int:id>/delete/", HomeOwnerDeleteAPIView.as_view(), name="homeowner-delete"),
]
