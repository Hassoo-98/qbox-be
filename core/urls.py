from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve

schema_view = get_schema_view(
    openapi.Info(
        title="Qbox API",
        default_version="v1",
        description="Qbox backend API documentation",
        contact=openapi.Contact(email="support@qbox.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
  #  url="https://backend.qbox.sa/",  
    url="http://127.0.0.1:8000"
)
urlpatterns = [
   
    path("admin/", admin.site.urls),

    path("auth/", include("accounts.urls")),
    path("staff/", include("staff.urls")),
    path("driver/", include("driver.urls")),
    path("home_owner/", include("home_owner.urls")),
    path("qbox/", include("q_box.urls")),
    path("packages/", include("packages.urls")),
    path("service_provider/", include("service_provider.urls")),
    path("locations/", include("locations.urls")),
    path("promotion/", include("promotion.urls")),
    path("media/", include("media.urls")),
    path("timelines/",include("package_timeline.urls")),
      re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
   
    re_path(
        r"^swagger/schema/$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
