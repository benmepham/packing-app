from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CustomUserCreationForm, CustomAuthenticationForm


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect("core:dashboard")

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


def logout_view(request):
    """Handle user logout."""
    if request.method == "POST":
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect("accounts:login")


def register_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, "Account created successfully! Welcome to Packing App."
            )
            return redirect("core:dashboard")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})
