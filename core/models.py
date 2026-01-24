from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """A reusable category template containing packable items."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class CategoryItem(models.Model):
    """A template item within a category."""

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Trip(models.Model):
    """A trip with a packing checklist."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trips")
    name = models.CharField(max_length=200)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def progress(self):
        """Return packing progress as a dict with packed, total, and percentage."""
        items = self.items.all()
        total = items.count()
        packed = items.filter(is_packed=True).count()
        percentage = round((packed / total) * 100) if total > 0 else 0
        return {"packed": packed, "total": total, "percentage": percentage}


class TripCategory(models.Model):
    """Records which categories were selected for a trip."""

    trip = models.ForeignKey(
        Trip, on_delete=models.CASCADE, related_name="trip_categories"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trip_usages",
    )
    category_name = models.CharField(max_length=100)  # Preserved if category deleted

    class Meta:
        ordering = ["category_name"]

    def __str__(self):
        return f"{self.trip.name} - {self.category_name}"


class TripItem(models.Model):
    """An item in a trip's packing checklist."""

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="items")
    trip_category = models.ForeignKey(
        TripCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
    )
    name = models.CharField(max_length=200)
    is_packed = models.BooleanField(default=False)
    is_custom = models.BooleanField(default=False)  # True if added during trip
    source_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="derived_items",
        help_text="Original category this item came from or should be saved to",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["trip_category__category_name", "is_custom", "name"]

    def __str__(self):
        return f"{self.name} ({'packed' if self.is_packed else 'unpacked'})"
