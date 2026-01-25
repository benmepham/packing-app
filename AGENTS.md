# AI Agent Instructions for Packing App

This document provides context for AI coding agents working on this codebase.

## Project Overview

A Django-based packing list web application. Users create category templates with items, then generate trip-specific checklists.

## Tech Stack

- **Backend**: Django 6.x + Django REST Framework
- **Frontend**: Bootstrap 5 + vanilla JavaScript (no React/Vue/etc.)
- **Database**: SQLite
- **Package Manager**: uv (not pip)
- **Python**: 3.13+

## Build/Lint/Test Commands

### Using mise (preferred)

```bash
mise run dev           # Run development server
mise run migrate       # Run migrations
mise run db            # makemigrations + migrate
mise run test          # Run all tests
mise run test:verbose  # Run tests with verbose output
mise run check         # Run lint + format check + typecheck
mise run fix           # Auto-fix lint issues and format code
mise run lint          # Run ruff linter only
mise run lint:fix      # Fix auto-fixable lint issues
mise run format        # Format code with ruff
mise run format:check  # Check formatting without changes
mise run typecheck     # Run mypy only
mise run shell         # Open Django shell
mise run setup         # Initial setup (install, migrate, check)
```

### Running a Single Test

```bash
# Run a single test class
uv run python manage.py test core.tests.CategoryModelTest

# Run a single test method
uv run python manage.py test core.tests.CategoryModelTest.test_category_creation

# Run all tests in an app
uv run python manage.py test core
uv run python manage.py test accounts

# Run with verbosity
uv run python manage.py test core.tests.CategoryModelTest -v 2
```

Always run `mise run check` before committing.

## Code Style Guidelines

### Formatting & Linting (ruff)

- Line length: 100 characters
- Target Python: 3.13
- Migrations and staticfiles are excluded from linting

### Import Order (isort via ruff)

1. Standard library
2. Third-party packages (Django, DRF)
3. First-party packages (core, accounts, packing_project)

```python
# Good
from django.contrib.auth.models import User
from django.db import models
from rest_framework import serializers

from core.models import Category, Trip
from .models import CategoryItem
```

### Naming Conventions

- **Functions/methods**: `snake_case` (e.g., `get_queryset`, `trip_create`)
- **Classes**: `PascalCase` (e.g., `CategoryItem`, `TripDetailSerializer`)
- **Constants**: `UPPER_SNAKE_CASE`
- **Templates**: `snake_case.html` in `templates/<app>/` directories
- **URLs**: kebab-case paths, snake_case names (e.g., `path("trip-items/", ..., name="trip_items")`)

### Type Hints

- Use type hints for function signatures
- Mypy with django-stubs and djangorestframework-stubs is configured
- `strict = false` but `warn_return_any = true`

```python
def get_queryset(self) -> QuerySet[Trip]:
    return Trip.objects.filter(user=self.request.user)
```

### Django Patterns

**Models**:

- Always define `__str__` method
- Use docstrings for model classes
- Define `Meta` class with `ordering` and `verbose_name_plural` as needed
- Use `related_name` on ForeignKey fields

```python
class Category(models.Model):
    """A reusable category template containing packable items."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]
    
    def __str__(self):
        return self.name
```

**Views**:

- Use `@login_required` decorator for function-based views
- Use `get_object_or_404` with user filtering for ownership checks
- Keep views focused; use transactions for multi-step operations

**API Views**:

- Use DRF generics (ListCreateAPIView, RetrieveUpdateDestroyAPIView)
- Always set `permission_classes = [IsAuthenticated]`
- Filter querysets by user in `get_queryset()`

**Serializers**:

- Use docstrings to describe purpose
- Explicitly list fields (no `fields = "__all__"`)
- Mark computed fields as `read_only_fields`

### Error Handling

- Use Django's `get_object_or_404` for 404 responses
- Return appropriate HTTP status codes in API views
- Use `messages.success/error` for user feedback in template views

### Frontend Patterns

- Templates extend `base.html`
- Use `apiRequest()` helper from `static/js/app.js` for AJAX
- CSRF handled via `getCookie('csrftoken')`
- Bootstrap 5 classes for styling
- Prefer server-side rendering with AJAX enhancements

## Architecture

### Apps

- **accounts/**: User authentication (login, logout, registration)
- **core/**: Main app with categories, trips, and items
- **core/api/**: REST API using Django REST Framework

### Models (core/models.py)

- `Category`: Reusable category template (FK to User)
- `CategoryItem`: Template item in a category
- `Trip`: A trip with packing checklist (FK to User)
- `TripCategory`: Links trip to categories (preserves name if category deleted)
- `TripItem`: Actual checklist item (snapshot, not reference)

### Key Design Decisions

1. **Snapshot Items**: When creating a trip, items are copied from categories. Changes to categories don't affect existing trips.
2. **Custom Items**: Items added directly to a trip have `is_custom=True`. Users can save them to a category.
3. **Category Preservation**: `TripCategory.category_name` is denormalized to preserve the name if the category is deleted.

### URL Structure

- `/accounts/login/`, `/accounts/register/`, `/accounts/logout/`
- `/` - Dashboard
- `/categories/` - Category list with inline item management
- `/trips/` - Trip list
- `/trips/create/` - Create trip with category selection
- `/trips/<id>/` - Trip detail/checklist
- `/api/...` - REST API endpoints

### Frontend Patterns

- Templates extend `base.html` which includes Bootstrap 5 and custom JS
- AJAX interactions use `apiRequest()` helper in `static/js/app.js`
- CSRF token is handled by `getCookie('csrftoken')`
- Forms use Bootstrap classes for styling

### API Authentication

Uses Django session authentication. All API endpoints require authenticated user.

## Common Tasks

### Adding a New Field to a Model

1. Add field to model in `core/models.py`
2. Run `uv run python manage.py makemigrations`
3. Run `uv run python manage.py migrate`
4. Update serializers in `core/api/serializers.py` if needed
5. Update views/templates as needed

### Adding a New View

1. Add view function/class to `core/views.py`
2. Add URL pattern to `core/urls.py`
3. Create template in `templates/core/`
4. Update navigation in `base.html` if needed

### Adding a New API Endpoint

1. Add serializer to `core/api/serializers.py`
2. Add view to `core/api/views.py`
3. Add URL pattern to `core/api/urls.py`

## Testing

Tests should cover:

- Model methods and properties
- View authorization (users can only see their own data)
- API endpoints

Test file location: `<app>/tests.py` (e.g., `core/tests.py`, `accounts/tests.py`)

## Git Commits

Always make commits as you go.

Always include this footer in commit messages:

```
🤖 AI assisted using OpenCode
```
