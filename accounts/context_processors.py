"""Template context processors for the accounts app."""

from django.conf import settings
from django.http import HttpRequest


def auth_settings(request: HttpRequest) -> dict:
    """
    Add authentication settings to template context.

    Makes auth configuration available in templates for conditional rendering
    of login options (OIDC button, password form, registration link).

    Returns:
        Dict with auth settings:
        - oidc_enabled: Whether OIDC authentication is enabled
        - password_login_enabled: Whether username/password login is enabled
    """
    return {
        "oidc_enabled": getattr(settings, "OIDC_ENABLED", False),
        "password_login_enabled": getattr(settings, "PASSWORD_LOGIN_ENABLED", True),
    }
