from django.conf import settings
from django.urls import URLPattern, URLResolver, include, path

from . import views

app_name = "accounts"

urlpatterns: list[URLPattern | URLResolver] = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
]

# Include OIDC URLs when OIDC authentication is enabled
if getattr(settings, "OIDC_ENABLED", False):
    urlpatterns += [
        path("oidc/", include("mozilla_django_oidc.urls")),
    ]
