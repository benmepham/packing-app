# AI Agent Instructions for Packing App

## Project Overview

A Django-based packing list web application. Users create category templates with items, then generate trip-specific checklists.

## Tech Stack

- **Backend**: Django 6.x + Django REST Framework
- **Frontend**: Bootstrap 5 + vanilla JavaScript (no React/Vue/etc.)
- **Database**: SQLite
- **Package Managers**: uv (Python), pnpm (JavaScript)
- **Python**: 3.13+

## Essential Commands

All commands are defined in `mise.toml`. Key commands:

```bash
mise run check   # Run all checks (lint, format, typecheck) - run before committing
mise run fix     # Auto-fix lint/format issues
mise run test    # Run all tests
mise run db      # makemigrations + migrate
mise run dev     # Run development server
```

Run `mise tasks` to see all available commands.

### Running a Single Test

```bash
uv run python manage.py test core.tests.CategoryModelTest.test_category_creation
```

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

- `/accounts/` - Authentication (login, register, logout)
- `/` - Dashboard
- `/categories/` - Category list with inline item management
- `/trips/` - Trip list and CRUD
- `/api/...` - REST API endpoints

## Code Style

Configs: `pyproject.toml` (ruff, mypy, djlint), `biome.json` (JS/CSS)

### Naming Conventions

- **Functions/methods**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Templates**: `snake_case.html` in `templates/<app>/`
- **URLs**: kebab-case paths, snake_case names (e.g., `path("trip-items/", ..., name="trip_items")`)

### Type Hints

Use type hints for function signatures. Mypy with django-stubs is configured.

```python
def get_queryset(self) -> QuerySet[Trip]:
    return Trip.objects.filter(user=self.request.user)
```

### Django Patterns

**Models**: Define `__str__`, use docstrings, set `Meta.ordering`, use `related_name` on ForeignKeys.

**Views**: Use `@login_required`, filter by user with `get_object_or_404`.

**API Views**: Use DRF generics, set `permission_classes = [IsAuthenticated]`, filter querysets by user.

**Serializers**: Use docstrings, explicitly list fields (no `fields = "__all__"`).

### Frontend Patterns

- Templates extend `base.html`
- Use `apiRequest()` helper from `static/js/app.js` for AJAX
- CSRF handled via `getCookie('csrftoken')`
- Bootstrap 5 classes for styling
- Prefer server-side rendering with AJAX enhancements

## Testing

Test file location: `<app>/tests.py`

Tests should cover:
- Model methods and properties
- View authorization (users can only see their own data)
- API endpoints

## Git Commits

Always make commits as you go.

Always include this footer in commit messages:

```
AI assisted using OpenCode
```
