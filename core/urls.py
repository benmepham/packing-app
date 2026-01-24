from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/<int:pk>/", views.category_detail, name="category_detail"),
    path("trips/", views.trip_list, name="trip_list"),
    path("trips/create/", views.trip_create, name="trip_create"),
    path("trips/<int:pk>/", views.trip_detail, name="trip_detail"),
    path("trips/<int:pk>/complete/", views.trip_complete, name="trip_complete"),
    path("trips/<int:pk>/delete/", views.trip_delete, name="trip_delete"),
]
