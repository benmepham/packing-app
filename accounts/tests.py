from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.oidc import PocketIDAuthBackend as OIDCAuthBackend

# Use simple staticfiles storage for tests (avoids manifest requirement)
TEST_STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


@override_settings(STORAGES=TEST_STORAGES)
class LoginViewTest(TestCase):
    """Tests for the login view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.url = reverse("accounts:login")

    def test_login_page_renders(self):
        """Test that the login page renders correctly."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_success(self):
        """Test successful login redirects to dashboard."""
        response = self.client.post(self.url, {"username": "testuser", "password": "testpass"})
        self.assertRedirects(response, reverse("core:dashboard"))

        # Verify user is logged in
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_login_with_valid_next_url(self):
        """Test login redirects to valid next URL."""
        next_url = reverse("core:trip_list")
        response = self.client.post(
            f"{self.url}?next={next_url}", {"username": "testuser", "password": "testpass"}
        )
        self.assertRedirects(response, next_url)

    def test_login_rejects_external_redirect(self):
        """Test login rejects external URLs to prevent open redirect attacks."""
        response = self.client.post(
            f"{self.url}?next=https://evil.com", {"username": "testuser", "password": "testpass"}
        )
        # Should redirect to dashboard instead of external URL
        self.assertRedirects(response, reverse("core:dashboard"))

    @override_settings(PASSWORD_LOGIN_ENABLED=False, OIDC_ENABLED=False)
    def test_login_with_password_disabled_shows_error(self):
        """Test that disabling password login without OIDC shows an error message."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # When password login is disabled but OIDC isn't configured, show error
        self.assertContains(response, "Password login is disabled")


@override_settings(STORAGES=TEST_STORAGES)
class RegisterViewTest(TestCase):
    """Tests for the registration view."""

    def setUp(self):
        self.client = Client()
        self.url = reverse("accounts:register")

    def test_register_page_renders(self):
        """Test that the registration page renders correctly."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_register_creates_user_and_logs_in(self):
        """Test that registration creates a user and logs them in."""
        response = self.client.post(
            self.url,
            {
                "username": "newuser",
                "password1": "complexpass123!",
                "password2": "complexpass123!",
            },
        )
        self.assertRedirects(response, reverse("core:dashboard"))

        # Verify user was created
        self.assertTrue(User.objects.filter(username="newuser").exists())

        # Verify user is logged in
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)


@override_settings(STORAGES=TEST_STORAGES)
class LogoutViewTest(TestCase):
    """Tests for the logout view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.url = reverse("accounts:logout")

    def test_logout_redirects_to_login(self):
        """Test that logout redirects to login page."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("accounts:login"))

        # Verify user is logged out (dashboard requires login)
        response = self.client.get(reverse("core:dashboard"))
        self.assertRedirects(response, f"/accounts/login/?next={reverse('core:dashboard')}")


# OIDC settings required for instantiating the backend
OIDC_TEST_SETTINGS = {
    "OIDC_OP_TOKEN_ENDPOINT": "https://example.com/token",
    "OIDC_OP_USER_ENDPOINT": "https://example.com/userinfo",
    "OIDC_OP_JWKS_ENDPOINT": "https://example.com/.well-known/jwks.json",
    "OIDC_RP_CLIENT_ID": "test-client-id",
    "OIDC_RP_CLIENT_SECRET": "test-client-secret",
    "OIDC_RP_SIGN_ALGO": "RS256",
    "OIDC_ADMIN_GROUP": "admin",
    "OIDC_STAFF_GROUP": "staff",
}


@override_settings(**OIDC_TEST_SETTINGS)
class OIDCAuthBackendTest(TestCase):
    """Tests for the custom OIDC authentication backend."""

    def setUp(self):
        self.backend = OIDCAuthBackend()

    def test_filter_users_by_claims_finds_existing_user(self):
        """Test that filter_users_by_claims finds a user by preferred_username."""
        user = User.objects.create_user(username="oidcuser", email="oidc@example.com")

        claims = {"preferred_username": "oidcuser", "email": "oidc@example.com"}
        result = self.backend.filter_users_by_claims(claims)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], user)

    def test_filter_users_by_claims_returns_empty_for_unknown_user(self):
        """Test that filter_users_by_claims returns empty list for unknown username."""
        claims = {"preferred_username": "unknownuser", "email": "unknown@example.com"}
        result = self.backend.filter_users_by_claims(claims)

        self.assertEqual(result, [])

    def test_filter_users_by_claims_returns_empty_when_no_username(self):
        """Test that filter_users_by_claims returns empty list when preferred_username is missing."""
        claims = {"email": "nousername@example.com"}
        result = self.backend.filter_users_by_claims(claims)

        self.assertEqual(result, [])

    def test_create_user_from_claims(self):
        """Test that create_user creates a Django user from OIDC claims."""
        claims = {
            "preferred_username": "newoidcuser",
            "email": "newoidc@example.com",
            "given_name": "New",
            "family_name": "User",
        }

        user = self.backend.create_user(claims)

        self.assertIsNotNone(user)
        self.assertEqual(user.username, "newoidcuser")
        self.assertEqual(user.email, "newoidc@example.com")
        self.assertEqual(user.first_name, "New")
        self.assertEqual(user.last_name, "User")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_returns_none_without_username(self):
        """Test that create_user returns None if preferred_username is missing."""
        claims = {"email": "nousername@example.com"}

        user = self.backend.create_user(claims)

        self.assertIsNone(user)

    def test_update_user_syncs_profile_data(self):
        """Test that update_user syncs profile data from claims."""
        user = User.objects.create_user(
            username="existinguser",
            email="old@example.com",
            first_name="Old",
            last_name="Name",
        )

        claims = {
            "preferred_username": "existinguser",
            "email": "new@example.com",
            "given_name": "New",
            "family_name": "Name",
        }

        updated_user = self.backend.update_user(user, claims)

        self.assertEqual(updated_user.email, "new@example.com")
        self.assertEqual(updated_user.first_name, "New")
        self.assertEqual(updated_user.last_name, "Name")

    @override_settings(OIDC_ADMIN_GROUP="admins", OIDC_STAFF_GROUP="staff")
    def test_update_user_sets_superuser_from_admin_group(self):
        """Test that update_user sets is_superuser when user is in admin group."""
        user = User.objects.create_user(username="adminuser")

        claims = {"preferred_username": "adminuser", "groups": ["admins"]}

        updated_user = self.backend.update_user(user, claims)

        self.assertTrue(updated_user.is_superuser)
        self.assertTrue(updated_user.is_staff)  # Admin group also grants staff

    @override_settings(OIDC_ADMIN_GROUP="admins", OIDC_STAFF_GROUP="staff")
    def test_update_user_sets_staff_from_staff_group(self):
        """Test that update_user sets is_staff when user is in staff group."""
        user = User.objects.create_user(username="staffuser")

        claims = {"preferred_username": "staffuser", "groups": ["staff"]}

        updated_user = self.backend.update_user(user, claims)

        self.assertFalse(updated_user.is_superuser)
        self.assertTrue(updated_user.is_staff)

    @override_settings(OIDC_ADMIN_GROUP="admins", OIDC_STAFF_GROUP="staff")
    def test_update_user_removes_admin_when_not_in_group(self):
        """Test that update_user removes admin status when user is no longer in admin group."""
        user = User.objects.create_user(username="formeradmin")
        user.is_superuser = True
        user.is_staff = True
        user.save()

        claims = {"preferred_username": "formeradmin", "groups": []}

        updated_user = self.backend.update_user(user, claims)

        self.assertFalse(updated_user.is_superuser)
        self.assertFalse(updated_user.is_staff)

    @override_settings(OIDC_ADMIN_GROUP="admins", OIDC_STAFF_GROUP="staff")
    def test_create_user_sets_admin_from_groups(self):
        """Test that create_user sets admin status from groups claim."""
        claims = {
            "preferred_username": "newadmin",
            "email": "newadmin@example.com",
            "groups": ["admins"],
        }

        user = self.backend.create_user(claims)

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
