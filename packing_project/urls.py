"""
URL configuration for packing_project project.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("api/", include("core.api.urls")),
    path("", include("core.urls")),
]

# Include OIDC URLs at root level (not namespaced) because mozilla_django_oidc
# internally uses non-namespaced URL names for reversing
if getattr(settings, "OIDC_ENABLED", False):
    urlpatterns.insert(1, path("accounts/oidc/", include("mozilla_django_oidc.urls")))
