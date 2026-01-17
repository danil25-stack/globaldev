from django.contrib import admin
from django.urls import include, path
from drf_spectacular import views


urlpatterns = [
    path("api/v1/admin/", admin.site.urls),
    path("api/v1/auth/", include("djoser.urls")),
    path("api/v1/auth/", include("djoser.urls.jwt")),
    path("api/v1/schema/", views.SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/", views.SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/redoc/", views.SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/exchange/", include("exchange.urls")),
]
