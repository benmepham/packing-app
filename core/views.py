from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import Category, CategoryItem, Trip, TripCategory, TripItem
from .forms import CategoryForm, TripForm


@login_required
def dashboard(request):
    """Display the main dashboard with stats and recent trips."""
    trips = Trip.objects.filter(user=request.user)
    active_trips = trips.filter(is_complete=False)[:5]
    completed_trips = trips.filter(is_complete=True)[:5]
    categories = Category.objects.filter(user=request.user)

    context = {
        "active_trips": active_trips,
        "completed_trips": completed_trips,
        "total_trips": trips.count(),
        "total_categories": categories.count(),
        "total_active": trips.filter(is_complete=False).count(),
    }
    return render(request, "core/dashboard.html", context)


@login_required
def category_list(request):
    """List all categories with inline item management."""
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f"Category '{category.name}' created.")
            return redirect("core:category_list")
    else:
        form = CategoryForm()

    categories = Category.objects.filter(user=request.user).prefetch_related("items")
    context = {"categories": categories, "form": form}
    return render(request, "core/categories/list.html", context)


@login_required
def category_detail(request, pk):
    """View and edit a single category."""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    context = {"category": category}
    return render(request, "core/categories/detail.html", context)


@login_required
def trip_list(request):
    """List all trips."""
    trips = Trip.objects.filter(user=request.user)
    active_trips = trips.filter(is_complete=False)
    completed_trips = trips.filter(is_complete=True)

    context = {
        "active_trips": active_trips,
        "completed_trips": completed_trips,
    }
    return render(request, "core/trips/list.html", context)


@login_required
def trip_create(request):
    """Create a new trip with category selection."""
    template_trip = None
    template_id = request.GET.get("template")
    if template_id:
        template_trip = Trip.objects.filter(pk=template_id, user=request.user).first()

    if request.method == "POST":
        form = TripForm(request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                trip = Trip.objects.create(
                    user=request.user,
                    name=form.cleaned_data["name"],
                )

                # Create trip categories and items from selected categories
                selected_categories = form.cleaned_data["categories"]
                for category in selected_categories:
                    trip_category = TripCategory.objects.create(
                        trip=trip,
                        category=category,
                        category_name=category.name,
                    )
                    # Snapshot items from category
                    for item in category.items.all():
                        TripItem.objects.create(
                            trip=trip,
                            trip_category=trip_category,
                            name=item.name,
                            source_category=category,
                        )

                # If using template, also copy custom items
                if template_trip:
                    custom_items = template_trip.items.filter(is_custom=True)
                    for item in custom_items:
                        TripItem.objects.create(
                            trip=trip,
                            name=item.name,
                            is_custom=True,
                            source_category=item.source_category,
                        )

            messages.success(
                request, f"Trip '{trip.name}' created with {trip.items.count()} items."
            )
            return redirect("core:trip_detail", pk=trip.pk)
    else:
        initial = {}
        if template_trip:
            # Pre-select categories from template
            template_categories = template_trip.trip_categories.filter(
                category__isnull=False
            ).values_list("category", flat=True)
            initial["categories"] = Category.objects.filter(
                pk__in=template_categories, user=request.user
            )
        form = TripForm(user=request.user, initial=initial)

    # Get existing trips for template selection
    existing_trips = Trip.objects.filter(user=request.user)

    context = {
        "form": form,
        "existing_trips": existing_trips,
        "template_trip": template_trip,
    }
    return render(request, "core/trips/create.html", context)


@login_required
def trip_detail(request, pk):
    """View trip checklist and manage items."""
    trip = get_object_or_404(Trip, pk=pk, user=request.user)

    # Group items by category
    trip_categories = trip.trip_categories.prefetch_related("items")
    custom_items = trip.items.filter(is_custom=True, trip_category__isnull=True)

    # Get user's categories for "add to category" dropdown
    categories = Category.objects.filter(user=request.user)

    context = {
        "trip": trip,
        "trip_categories": trip_categories,
        "custom_items": custom_items,
        "categories": categories,
    }
    return render(request, "core/trips/detail.html", context)


@login_required
def trip_complete(request, pk):
    """Mark a trip as complete or incomplete."""
    trip = get_object_or_404(Trip, pk=pk, user=request.user)

    if request.method == "POST":
        trip.is_complete = not trip.is_complete
        trip.save()
        status = "completed" if trip.is_complete else "reopened"
        messages.success(request, f"Trip '{trip.name}' has been {status}.")

    return redirect("core:trip_detail", pk=trip.pk)


@login_required
def trip_delete(request, pk):
    """Delete a trip."""
    trip = get_object_or_404(Trip, pk=pk, user=request.user)

    if request.method == "POST":
        name = trip.name
        trip.delete()
        messages.success(request, f"Trip '{name}' has been deleted.")
        return redirect("core:trip_list")

    return redirect("core:trip_detail", pk=trip.pk)
