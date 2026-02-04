from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Qbox API",
        description="Qbox backend API documentation",
        default_version='v1',
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@qbox.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth", include("accounts.urls")),
    path("api/staff", include("staff.urls")),
    path("api/driver", include("driver.urls")),
    path("api/home_owner", include("home_owner.urls")),
    path("api/q_box", include("q_box.urls")),
    path("api/packages", include("packages.urls")),
    path("api/service_provider", include("service_provider.urls")),
    path("api/locations", include("locations.urls")),
    # Swagger URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger/schema/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger'),
]
