import logging

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)

# Guard against multiple executions of ready()
_startup_logged = False


class CoreConfig(AppConfig):
    """Core application configuration with startup logging."""

    name = "core"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """Log configuration on application startup."""
        # Guard against multiple executions (Django can call ready() multiple times)
        global _startup_logged
        if not _startup_logged:
            _startup_logged = True
            self._log_startup_config()

    def _log_startup_config(self):
        """Log important configuration settings at startup."""
        logger.info("=" * 60)
        logger.info("Packing App Configuration")
        logger.info("=" * 60)

        # Core settings
        logger.info("Core Settings:")
        logger.info("  Debug Mode: %s", settings.DEBUG)
        logger.info("  Database: %s", settings.DATABASES["default"]["NAME"])
        logger.info("  Allowed Hosts: %s", ", ".join(settings.ALLOWED_HOSTS))
        logger.info("  Secure Cookies: %s", settings.SESSION_COOKIE_SECURE)

        # Authentication settings
        logger.info("")
        logger.info("Authentication:")
        password_login = getattr(settings, "PASSWORD_LOGIN_ENABLED", True)
        oidc_enabled = getattr(settings, "OIDC_ENABLED", False)

        logger.info("  Password Login: %s", "Enabled" if password_login else "Disabled")
        logger.info("  OIDC/SSO: %s", "Enabled" if oidc_enabled else "Disabled")

        # OIDC details (only if enabled)
        if oidc_enabled:
            logger.info("")
            logger.info("OIDC Configuration:")
            oidc_base_url = getattr(settings, "OIDC_OP_BASE_URL", "")
            oidc_client_id = getattr(settings, "OIDC_RP_CLIENT_ID", "")
            oidc_client_secret = getattr(settings, "OIDC_RP_CLIENT_SECRET", "")
            oidc_admin_group = getattr(settings, "OIDC_ADMIN_GROUP", "admin")
            oidc_staff_group = getattr(settings, "OIDC_STAFF_GROUP", "staff")

            logger.info("  Provider: %s", oidc_base_url if oidc_base_url else "(not configured)")
            logger.info("  Client ID: %s", oidc_client_id if oidc_client_id else "(not configured)")
            logger.info("  Client Secret: %s", self._mask_secret(oidc_client_secret))
            logger.info("  Admin Group: %s", oidc_admin_group)
            logger.info("  Staff Group: %s", oidc_staff_group)

        logger.info("=" * 60)

    @staticmethod
    def _mask_secret(secret: str) -> str:
        """
        Mask a secret string for logging.

        Shows first 3 and last 3 characters with *** in the middle.

        Args:
            secret: The secret string to mask

        Returns:
            Masked string or "(not configured)" if empty
        """
        if not secret:
            return "(not configured)"
        if len(secret) <= 6:
            return "***"
        return f"{secret[:3]}***{secret[-3:]}"
