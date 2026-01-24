from rest_framework import serializers

from ..models import Category, CategoryItem, Trip, TripCategory, TripItem


class CategoryItemSerializer(serializers.ModelSerializer):
    """Serializer for category items."""

    class Meta:
        model = CategoryItem
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category list/create."""

    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "item_count", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_item_count(self, obj):
        return obj.items.count()


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


class TripSerializer(serializers.ModelSerializer):
    """Serializer for trip list/create."""

    progress = serializers.ReadOnlyField()

    class Meta:
        model = Trip
        fields = ["id", "name", "is_complete", "progress", "created_at"]
        read_only_fields = ["id", "created_at"]


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
