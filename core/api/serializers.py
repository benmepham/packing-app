from rest_framework import serializers

from ..models import Category, CategoryItem, Trip, TripCategory, TripItem


class CategoryImportItemSerializer(serializers.Serializer):
    """Serializer for a single row in the CSV import."""

    category = serializers.CharField(max_length=100)
    item = serializers.CharField(max_length=100)


class CategoryImportSerializer(serializers.Serializer):
    """Serializer for bulk importing categories and items from CSV."""

    items = CategoryImportItemSerializer(many=True)

    def validate_items(self, value: list[dict]) -> list[dict]:
        """Validate that items list is not empty."""
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        return value


class CategoryItemSerializer(serializers.ModelSerializer):
    """Serializer for category items."""

    class Meta:
        model = CategoryItem
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Serializer for category detail with nested items."""

    items = CategoryItemSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "items", "created_at"]
        read_only_fields = ["id", "created_at"]


class TripItemSerializer(serializers.ModelSerializer):
    """Serializer for trip items."""

    category_name = serializers.CharField(
        source="trip_category.category_name", read_only=True, allow_null=True
    )

    class Meta:
        model = TripItem
        fields = [
            "id",
            "name",
            "is_packed",
            "is_custom",
            "category_name",
            "source_category",
            "created_at",
        ]
        read_only_fields = ["id", "is_custom", "category_name", "created_at"]


class TripCategorySerializer(serializers.ModelSerializer):
    """Serializer for trip categories."""

    items = TripItemSerializer(many=True, read_only=True)

    class Meta:
        model = TripCategory
        fields = ["id", "category_name", "category", "items"]
        read_only_fields = ["id"]


class TripDetailSerializer(serializers.ModelSerializer):
    """Serializer for trip detail with nested categories and items."""

    trip_categories = TripCategorySerializer(many=True, read_only=True)
    progress = serializers.ReadOnlyField()

    class Meta:
        model = Trip
        fields = [
            "id",
            "name",
            "is_complete",
            "progress",
            "trip_categories",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
