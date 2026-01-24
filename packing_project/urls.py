"""
URL configuration for packing_project project.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("api/", include("core.api.urls")),
    path("", include("core.urls")),
]
