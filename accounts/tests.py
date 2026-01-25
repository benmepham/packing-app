from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse

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
