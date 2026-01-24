# AI Agent Instructions for Packing App

This document provides context for AI coding agents working on this codebase.

## Project Overview

A Django-based packing list web application. Users create category templates with items, then generate trip-specific checklists.

## Tech Stack

- **Backend**: Django 6.x + Django REST Framework
- **Frontend**: Bootstrap 5 + vanilla JavaScript (no React/Vue/etc.)
- **Database**: SQLite
- **Package Manager**: uv (not pip)

## Key Commands

```bash
# Install dependencies
uv sync

# Run development server
uv run python manage.py runserver

# Run migrations
uv run python manage.py migrate

# Create migrations after model changes
uv run python manage.py makemigrations

# Run tests
uv run python manage.py test

# Django system check
uv run python manage.py check
```

### Using Task

This project uses [Task](https://taskfile.dev/) for running common commands:

```bash
task dev           # Run development server
task migrate       # Run migrations
task db            # makemigrations + migrate
task test          # Run tests
task check         # Run lint + format check + typecheck
task fix           # Auto-fix lint issues and format code
task lint          # Run ruff linter only
task typecheck     # Run mypy only
```

### Linting and Type Checking

- **Ruff**: Used for linting and formatting (configured in `pyproject.toml`)
- **Mypy**: Used for type checking with django-stubs

Always run `task check` before committing to ensure code quality.

## Architecture

### Apps

- **accounts/**: User authentication (login, logout, registration)
- **core/**: Main app with categories, trips, and items
- **core/api/**: REST API using Django REST Framework

### Models (core/models.py)

- `Category`: Reusable category template (FK to User)
- `CategoryItem`: Template item in a category
- `Trip`: A trip with packing checklist (FK to User)
- `TripCategory`: Links trip to categories used (preserves name if category deleted)
- `TripItem`: Actual checklist item (snapshot, not reference)

### Key Design Decisions

1. **Snapshot Items**: When creating a trip, items are copied from categories. Changes to categories don't affect existing trips.

2. **Template Feature**: When using a trip as template:
   - Pre-selects the same categories
   - Copies custom items (`is_custom=True`)

3. **Custom Items**: Items added directly to a trip have `is_custom=True`. Users can optionally save them to a category for future trips.

4. **Category Preservation**: `TripCategory.category_name` is denormalized so the category name is preserved if the category is deleted.

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

## Code Style

- Use Django conventions (snake_case for functions, PascalCase for classes)
- Keep templates simple - use Django template language, not complex JS
- Prefer server-side rendering with AJAX enhancements
- Use Bootstrap 5 classes for styling

## Testing

Run tests with `uv run python manage.py test`. Tests should cover:
- Model methods and properties
- View authorization (users can only see their own data)
- API endpoints

## Updating Documentation

Update README.md and AGENTS.md where relevant.

## Git Commits

Always make commits as you go.

Always include this footer in commit messages:

```
🤖 AI assisted using OpenCode
```
