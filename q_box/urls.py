from django.urls import path
from .views import (
    QboxListAPIView, QboxDetailAPIView, QboxByIdAPIView,
    QboxCreateAPIView, QboxUpdateAPIView, QboxDeleteAPIView
)

urlpatterns = [
    path('/', QboxListAPIView.as_view(), name='qbox-list'),
    path('/create/', QboxCreateAPIView.as_view(), name='qbox-create'),
    path('/<uuid:id>/', QboxDetailAPIView.as_view(), name='qbox-detail'),
    path('/<uuid:id>/update/', QboxUpdateAPIView.as_view(), name='qbox-update'),
    path('/<uuid:id>/delete/', QboxDeleteAPIView.as_view(), name='qbox-delete'),
    path('/by-qbox-id/<str:qbox_id>/', QboxByIdAPIView.as_view(), name='qbox-by-id'),
]
