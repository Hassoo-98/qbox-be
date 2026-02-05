from django.urls import path
from .views import ServiceProviderListCreateView, ServiceProviderDetailView, ServiceProviderApprovalView

urlpatterns = [
    path('', ServiceProviderListCreateView.as_view(), name='service-provider-list-create'),
    path('<int:pk>', ServiceProviderDetailView.as_view(), name='service-provider-detail'),
    path('<int:pk>/approve', ServiceProviderApprovalView.as_view(), name='service-provider-approve'),
]
