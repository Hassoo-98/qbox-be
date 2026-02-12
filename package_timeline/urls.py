from django.urls import path
from .views import (
    PackageTimeListItemView,
    PackageTimelineByPackageIdView,
    PackageTimelineDetailView,
)
urlPatterns=[
    path("",PackageTimeListItemView.as_view(),name="package-timeline-list"),
    path("<int:pk>",PackageTimelineDetailView.as_view(),name="package-timeline-details"),
    path("package/<int:package_id>",PackageTimelineByPackageIdView.as_view(),name="time-by-package-id")

]