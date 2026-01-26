"""Custom OIDC authentication backend with username matching and group sync."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.contrib.auth import get_user_model
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

if TYPE_CHECKING:
    from django.contrib.auth.models import User as UserType

logger = logging.getLogger(__name__)
User = get_user_model()


class PocketIDAuthBackend(OIDCAuthenticationBackend):
    """
    Custom OIDC authentication backend.

    Compatible with any OIDC provider (tested with Pocket ID).

    Features:
    - Matches users by username (from preferred_username claim)
    - Syncs profile data (email, first_name, last_name) on each login
    - Maps OIDC groups to Django staff/superuser status
    """

    def filter_users_by_claims(self, claims: dict[str, Any]):  # type: ignore[override]
        """
        Find existing users by username from OIDC claims.

        Args:
            claims: OIDC claims from the userinfo endpoint

        Returns:
            List of matching users (should be 0 or 1)
        """
        username = claims.get("preferred_username")
        if not username:
            logger.warning("OIDC claims missing preferred_username")
            return []

        try:
            user = User.objects.get(username=username)
            return [user]
        except User.DoesNotExist:
            return []

    def create_user(self, claims: dict[str, Any]) -> UserType | None:
        """
        Create a new Django user from OIDC claims.

        Args:
            claims: OIDC claims from the userinfo endpoint

        Returns:
            The newly created user
        """
        username = claims.get("preferred_username")
        email = claims.get("email", "")
        first_name = claims.get("given_name", "")
        last_name = claims.get("family_name", "")

        if not username:
            logger.error("Cannot create user: preferred_username claim is missing")
            return None

        user = User.objects.create_user(  # type: ignore[attr-defined]
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        # Set admin/staff status based on groups
        self._sync_groups(user, claims)

        logger.info("Created new user from OIDC: %s", username)
        return user

    def update_user(self, user, claims: dict):
        """
        Update existing user with data from OIDC claims.

        Called on each login to sync profile data and group membership.

        Args:
            user: The existing Django user
            claims: OIDC claims from the userinfo endpoint

        Returns:
            The updated user
        """
        # Sync profile fields
        user.email = claims.get("email", user.email)
        user.first_name = claims.get("given_name", user.first_name)
        user.last_name = claims.get("family_name", user.last_name)

        # Sync admin/staff status based on groups
        self._sync_groups(user, claims)

        user.save()
        logger.debug("Updated user from OIDC: %s", user.username)
        return user

    def _sync_groups(self, user, claims: dict) -> None:
        """
        Sync Django staff/superuser status based on OIDC groups claim.

        Args:
            user: The Django user to update
            claims: OIDC claims containing groups
        """
        groups = claims.get("groups", [])
        if not isinstance(groups, list):
            groups = []

        admin_group = getattr(settings, "OIDC_ADMIN_GROUP", "admin")
        staff_group = getattr(settings, "OIDC_STAFF_GROUP", "staff")

        # Superusers are in the admin group
        user.is_superuser = admin_group in groups

        # Staff are in either staff or admin group
        user.is_staff = staff_group in groups or admin_group in groups

        logger.debug(
            "Synced groups for %s: is_staff=%s, is_superuser=%s",
            user.username,
            user.is_staff,
            user.is_superuser,
        )
