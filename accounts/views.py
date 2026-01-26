from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import NoReverseMatch
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import CustomAuthenticationForm, CustomUserCreationForm


def login_view(request: HttpRequest) -> HttpResponse:
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    # If password login is disabled and OIDC is enabled, redirect to OIDC
    password_login_enabled = getattr(settings, "PASSWORD_LOGIN_ENABLED", True)
    oidc_enabled = getattr(settings, "OIDC_ENABLED", False)

    if not password_login_enabled and oidc_enabled:
        try:
            return redirect("oidc_authentication_init")
        except NoReverseMatch:
            # OIDC URLs not configured, fall through to error
            messages.error(
                request,
                "Password login is disabled but OIDC is not properly configured.",
            )
            return render(request, "accounts/login.html", {"form": None})

    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")

            # Validate redirect URL to prevent open redirect vulnerability
            next_url = request.GET.get("next", "")
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect("core:dashboard")
    else:
        form = CustomAuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Handle user logout.

    If the user logged in via OIDC (detected by session tokens),
    redirect to the OIDC logout endpoint to perform single-logout.
    Otherwise, perform standard Django logout.
    """
    if request.method == "POST":
        # Check if user has OIDC tokens in session (indicating OIDC login)
        oidc_enabled = getattr(settings, "OIDC_ENABLED", False)
        has_oidc_token = oidc_enabled and request.session.get("oidc_id_token") is not None

        # Perform Django logout first
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
