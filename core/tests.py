from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Category, CategoryItem, Trip, TripCategory, TripItem

# Use simple staticfiles storage for tests (avoids manifest requirement)
TEST_STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


class CategoryModelTest(TestCase):
    """Tests for the Category model."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.category = Category.objects.create(user=self.user, name="Electronics")

    def test_category_creation(self):
        """Test that a category can be created with required fields."""
        self.assertEqual(self.category.name, "Electronics")
        self.assertEqual(self.category.user, self.user)

    def test_category_str(self):
        """Test the string representation of a category."""
        self.assertEqual(str(self.category), "Electronics")


class TripModelTest(TestCase):
    """Tests for the Trip model and its progress property."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.trip = Trip.objects.create(user=self.user, name="Beach Vacation")

    def test_trip_creation(self):
        """Test that a trip can be created with required fields."""
        self.assertEqual(self.trip.name, "Beach Vacation")
        self.assertEqual(self.trip.user, self.user)
        self.assertFalse(self.trip.is_complete)

    def test_trip_str(self):
        """Test the string representation of a trip."""
        self.assertEqual(str(self.trip), "Beach Vacation")

    def test_trip_progress_empty(self):
        """Test progress calculation for a trip with no items."""
        progress = self.trip.progress
        self.assertEqual(progress["packed"], 0)
        self.assertEqual(progress["total"], 0)
        self.assertEqual(progress["percentage"], 0)

    def test_trip_progress_with_items(self):
        """Test progress calculation with packed and unpacked items."""
        # Create a trip category
        trip_category = TripCategory.objects.create(trip=self.trip, category_name="Clothes")
        # Create 4 items, 2 packed
        TripItem.objects.create(trip=self.trip, trip_category=trip_category, name="Shirt")
        TripItem.objects.create(trip=self.trip, trip_category=trip_category, name="Pants")
        TripItem.objects.create(
            trip=self.trip, trip_category=trip_category, name="Socks", is_packed=True
        )
        TripItem.objects.create(
            trip=self.trip, trip_category=trip_category, name="Hat", is_packed=True
        )

        progress = self.trip.progress
        self.assertEqual(progress["packed"], 2)
        self.assertEqual(progress["total"], 4)
        self.assertEqual(progress["percentage"], 50)


@override_settings(STORAGES=TEST_STORAGES)
class DashboardViewTest(TestCase):
    """Tests for the dashboard view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.other_user = User.objects.create_user(username="other", password="testpass")
        self.url = reverse("core:dashboard")

    def test_dashboard_requires_login(self):
        """Test that the dashboard requires authentication."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

    def test_dashboard_shows_user_data_only(self):
        """Test that the dashboard only shows the logged-in user's data."""
        # Create data for both users
        Trip.objects.create(user=self.user, name="My Trip")
        Trip.objects.create(user=self.other_user, name="Other Trip")
        Category.objects.create(user=self.user, name="My Category")
        Category.objects.create(user=self.other_user, name="Other Category")

        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        # Check that only user's trip count is shown
        self.assertEqual(response.context["total_trips"], 1)
        self.assertEqual(response.context["total_categories"], 1)


@override_settings(STORAGES=TEST_STORAGES)
class TripDetailViewTest(TestCase):
    """Tests for the trip detail view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.other_user = User.objects.create_user(username="other", password="testpass")
        self.trip = Trip.objects.create(user=self.user, name="My Trip")
        self.other_trip = Trip.objects.create(user=self.other_user, name="Other Trip")

    def test_trip_detail_requires_login(self):
        """Test that trip detail requires authentication."""
        url = reverse("core:trip_detail", args=[self.trip.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"/accounts/login/?next={url}")

    def test_trip_detail_ownership_check(self):
        """Test that users cannot view other users' trips."""
        self.client.login(username="testuser", password="testpass")

        # Can view own trip
        response = self.client.get(reverse("core:trip_detail", args=[self.trip.pk]))
        self.assertEqual(response.status_code, 200)

        # Cannot view other's trip (404)
        response = self.client.get(reverse("core:trip_detail", args=[self.other_trip.pk]))
        self.assertEqual(response.status_code, 404)


class CategoryAPITest(APITestCase):
    """Tests for the Category API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.other_user = User.objects.create_user(username="other", password="testpass")
        self.category = Category.objects.create(user=self.user, name="Electronics")
        self.other_category = Category.objects.create(user=self.other_user, name="Other")
        self.client = APIClient()

    def test_category_detail_requires_auth(self):
        """Test that API requires authentication."""
        url = reverse("api:category_detail", args=[self.category.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_detail_user_isolation(self):
        """Test that users can only access their own categories."""
        self.client.login(username="testuser", password="testpass")

        # Can access own category
        url = reverse("api:category_detail", args=[self.category.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Electronics")

        # Cannot access other's category (404)
        url = reverse("api:category_detail", args=[self.other_category.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_category_item_create(self):
        """Test creating a category item via API."""
        self.client.login(username="testuser", password="testpass")
        url = reverse("api:category_item_list", args=[self.category.pk])

        response = self.client.post(url, {"name": "Laptop"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CategoryItem.objects.count(), 1)
        self.assertEqual(CategoryItem.objects.first().name, "Laptop")


class TripItemAPITest(APITestCase):
    """Tests for the TripItem API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.trip = Trip.objects.create(user=self.user, name="Beach Trip")
        self.trip_category = TripCategory.objects.create(trip=self.trip, category_name="Clothes")
        self.item = TripItem.objects.create(
            trip=self.trip, trip_category=self.trip_category, name="Sunglasses"
        )
        self.client = APIClient()

    def test_trip_item_requires_auth(self):
        """Test that API requires authentication."""
        url = reverse("api:trip_item_list", args=[self.trip.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_trip_item_toggle_packed(self):
        """Test toggling the is_packed status of a trip item."""
        self.client.login(username="testuser", password="testpass")
        url = reverse("api:trip_item_detail", args=[self.trip.pk, self.item.pk])

        # Toggle to packed
        response = self.client.patch(url, {"is_packed": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertTrue(self.item.is_packed)

        # Toggle back to unpacked
        response = self.client.patch(url, {"is_packed": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertFalse(self.item.is_packed)

    def test_trip_item_create_is_custom(self):
        """Test that items created via API are marked as custom."""
        self.client.login(username="testuser", password="testpass")
        url = reverse("api:trip_item_list", args=[self.trip.pk])

        response = self.client.post(url, {"name": "Beach Towel"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_item = TripItem.objects.get(name="Beach Towel")
        self.assertTrue(new_item.is_custom)
