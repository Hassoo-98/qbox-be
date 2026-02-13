from django.urls import path
from .views import (
    PromotionsListView,
    PromotionDetailView,
    PromotionStatusView,
)

app_name = 'promotion'

urlpatterns = [
    path('', PromotionsListView.as_view(), name='promotion-list'),
    path('<uuid:pk>/', PromotionDetailView.as_view(), name='promotion-detail'),
    path('<uuid:pk>/status/', PromotionStatusView.as_view(), name='promotion-status'),
]
