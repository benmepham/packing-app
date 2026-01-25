from django.contrib import admin

from .models import Category, CategoryItem, Trip, TripCategory, TripItem


class CategoryItemInline(admin.TabularInline):
    model = CategoryItem
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "item_count", "created_at")
    list_filter = ("user",)
    search_fields = ("name",)
    inlines = [CategoryItemInline]

    @admin.display(description="Items")
    def item_count(self, obj: Category) -> int:
        return obj.items.count()


class TripItemInline(admin.TabularInline):
    model = TripItem
    extra = 0
    readonly_fields = ("is_custom", "source_category")


class TripCategoryInline(admin.TabularInline):
    model = TripCategory
    extra = 0
    readonly_fields = ("category_name",)


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "is_complete", "item_count", "created_at")
    list_filter = ("user", "is_complete")
    search_fields = ("name",)
    inlines = [TripCategoryInline, TripItemInline]

    @admin.display(description="Items")
    def item_count(self, obj: Trip) -> int:
        return obj.items.count()


@admin.register(CategoryItem)
class CategoryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "created_at")
    list_filter = ("category",)
    search_fields = ("name",)


@admin.register(TripItem)
class TripItemAdmin(admin.ModelAdmin):
    list_display = ("name", "trip", "is_packed", "is_custom", "created_at")
    list_filter = ("trip", "is_packed", "is_custom")
    search_fields = ("name",)
