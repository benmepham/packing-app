from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    # Categories
    path(
        "categories/import/",
        views.CategoryImportView.as_view(),
        name="category_import",
    ),
    path(
        "categories/<int:pk>/",
        views.CategoryDetailView.as_view(),
        name="category_detail",
    ),
    path(
        "categories/<int:category_pk>/items/",
        views.CategoryItemListCreateView.as_view(),
        name="category_item_list",
    ),
    path(
        "categories/<int:category_pk>/items/<int:pk>/",
        views.CategoryItemDetailView.as_view(),
        name="category_item_detail",
    ),
    # Trips
    path("trips/<int:pk>/", views.TripDetailView.as_view(), name="trip_detail"),
    path(
        "trips/<int:trip_pk>/items/",
        views.TripItemListCreateView.as_view(),
        name="trip_item_list",
    ),
    path(
        "trips/<int:trip_pk>/items/<int:pk>/",
        views.TripItemDetailView.as_view(),
        name="trip_item_detail",
    ),
    path(
        "trips/<int:trip_pk>/items/<int:pk>/add-to-category/",
        views.TripItemAddToCategoryView.as_view(),
        name="trip_item_add_to_category",
    ),
]
