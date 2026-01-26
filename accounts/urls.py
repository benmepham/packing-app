from django.urls import URLPattern, URLResolver, path

from . import views

app_name = "accounts"

urlpatterns: list[URLPattern | URLResolver] = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
]
