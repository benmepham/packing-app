from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import CustomAuthenticationForm, CustomUserCreationForm


def login_view(request: HttpRequest) -> HttpResponse:
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    # If password login is disabled and OIDC is enabled, redirect to OIDC
    password_login_enabled = getattr(settings, "PASSWORD_LOGIN_ENABLED", True)
    oidc_enabled = getattr(settings, "OIDC_ENABLED", False)

    if not password_login_enabled and oidc_enabled:
        return redirect("oidc_authentication_init")

    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get("next", "core:dashboard")
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request: HttpRequest) -> HttpResponse:
    """Handle user logout."""
    if request.method == "POST":
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect("accounts:login")


def register_view(request: HttpRequest) -> HttpResponse:
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to Packing App.")
            return redirect("core:dashboard")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})
