from django.urls import path
from .views import CityListCreateView, CityDetailView

urlpatterns = [
    path('', CityListCreateView.as_view(), name='city-list-create'),
    path('<int:pk>/', CityDetailView.as_view(), name='city-detail'),
]
