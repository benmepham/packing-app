from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Category, CategoryItem, Trip, TripItem
from .serializers import (
    CategoryDetailSerializer,
    CategoryImportSerializer,
    CategoryItemSerializer,
    TripDetailSerializer,
    TripItemSerializer,
)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a category."""

    serializer_class = CategoryDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class CategoryItemListCreateView(generics.ListCreateAPIView):
    """List or create items within a category."""

    serializer_class = CategoryItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        category = get_object_or_404(
            Category, pk=self.kwargs["category_pk"], user=self.request.user
        )
        return category.items.all()

    def perform_create(self, serializer):
        category = get_object_or_404(
            Category, pk=self.kwargs["category_pk"], user=self.request.user
        )
        serializer.save(category=category)


class CategoryItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a category item."""

    serializer_class = CategoryItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        category = get_object_or_404(
            Category, pk=self.kwargs["category_pk"], user=self.request.user
        )
        return category.items.all()


class TripDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a trip."""

    serializer_class = TripDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Trip.objects.filter(user=self.request.user)


class TripItemListCreateView(generics.ListCreateAPIView):
    """List or create items within a trip."""

    serializer_class = TripItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"], user=self.request.user)
        return trip.items.all()

    def perform_create(self, serializer):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"], user=self.request.user)
        serializer.save(trip=trip, is_custom=True)


class TripItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a trip item."""

    serializer_class = TripItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        trip = get_object_or_404(Trip, pk=self.kwargs["trip_pk"], user=self.request.user)
        return trip.items.all()


class TripItemAddToCategoryView(APIView):
    """Add a custom trip item to a category for future use."""

    permission_classes = [IsAuthenticated]

    def post(self, request, trip_pk, pk):
        trip = get_object_or_404(Trip, pk=trip_pk, user=request.user)
        item = get_object_or_404(TripItem, pk=pk, trip=trip)

        category_id = request.data.get("category_id")
        if not category_id:
            return Response(
                {"error": "category_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        category = get_object_or_404(Category, pk=category_id, user=request.user)

        # Check if item already exists in category
        if CategoryItem.objects.filter(category=category, name=item.name).exists():
            return Response(
                {"error": "Item already exists in this category"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create the category item
        CategoryItem.objects.create(category=category, name=item.name)

        # Update the trip item's source category
        item.source_category = category
        item.save()

        return Response({"success": True}, status=status.HTTP_201_CREATED)


class CategoryImportView(APIView):
    """Import categories and items from CSV data."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CategoryImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        items_data = serializer.validated_data["items"]
        user = request.user

        # Group items by category
        categories_map: dict[str, list[str]] = {}
        for row in items_data:
            category_name = row["category"].strip()
            item_name = row["item"].strip()
            if category_name not in categories_map:
                categories_map[category_name] = []
            if item_name not in categories_map[category_name]:
                categories_map[category_name].append(item_name)

        categories_created = 0
        categories_existing = 0
        items_created = 0
        items_skipped = 0

        with transaction.atomic():
            for category_name, item_names in categories_map.items():
                # Get or create category
                category, created = Category.objects.get_or_create(user=user, name=category_name)
                if created:
                    categories_created += 1
                else:
                    categories_existing += 1

                # Get existing item names for this category
                existing_items = set(category.items.values_list("name", flat=True))

                # Create new items
                for item_name in item_names:
                    if item_name in existing_items:
                        items_skipped += 1
                    else:
                        CategoryItem.objects.create(category=category, name=item_name)
                        items_created += 1
                        existing_items.add(item_name)

        return Response(
            {
                "categories_created": categories_created,
                "categories_existing": categories_existing,
                "items_created": items_created,
                "items_skipped": items_skipped,
            },
            status=status.HTTP_201_CREATED,
        )
