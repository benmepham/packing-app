from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from ..models import Category, CategoryItem, Trip, TripCategory, TripItem
from .serializers import (
    CategorySerializer,
    CategoryDetailSerializer,
    CategoryItemSerializer,
    TripSerializer,
    TripDetailSerializer,
    TripItemSerializer,
)


class CategoryListCreateView(generics.ListCreateAPIView):
    """List all categories or create a new one."""

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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


class TripListCreateView(generics.ListCreateAPIView):
    """List all trips or create a new one."""

    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Trip.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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
        trip = get_object_or_404(
            Trip, pk=self.kwargs["trip_pk"], user=self.request.user
        )
        return trip.items.all()

    def perform_create(self, serializer):
        trip = get_object_or_404(
            Trip, pk=self.kwargs["trip_pk"], user=self.request.user
        )
        serializer.save(trip=trip, is_custom=True)


class TripItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a trip item."""

    serializer_class = TripItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        trip = get_object_or_404(
            Trip, pk=self.kwargs["trip_pk"], user=self.request.user
        )
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
