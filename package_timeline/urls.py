from django.urls import path
from .views import (
    PackageTimeListItemView,
    PackageTimelineByPackageIdView,
    PackageTimelineDetailView,
)
urlpatterns=[
    path("",PackageTimeListItemView.as_view(),name="package-timeline-list"),
    path("<str:pk>",PackageTimelineDetailView.as_view(),name="package-timeline-details"),
    path("package/<str:package_id>",PackageTimelineByPackageIdView.as_view(),name="time-by-package-id")
]
