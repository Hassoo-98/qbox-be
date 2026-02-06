from django.urls import path
from .views import (
    QboxListAPIView,
    QboxDetailAPIView,
    QboxCreateAPIView,
    QboxUpdateAPIView,
    QboxStatusUpdateAPIView,
    QboxDeleteAPIView,
    VerifyQboxIdAPIView
)

urlpatterns = [
    path('/', QboxListAPIView.as_view(), name='qbox-list'),
    path('/create', QboxCreateAPIView.as_view(), name='qbox-create'),
    path('/<int:id>', QboxDetailAPIView.as_view(), name='qbox-detail'),
    path('/<int:id>/update', QboxUpdateAPIView.as_view(), name='qbox-update'),
    path('/<int:id>/change-status', QboxStatusUpdateAPIView.as_view(), name='qbox-status'),
    path('/<int:id>/delete', QboxDeleteAPIView.as_view(), name='qbox-delete'),
    path('/verify-id', VerifyQboxIdAPIView.as_view(), name='verify-qbox-id'),
]
