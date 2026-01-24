# Packing App

A Django web application for managing packing lists for trips. Create reusable category templates with items, then generate trip-specific checklists to track what you've packed.

## Features

- **User Authentication**: Self-registration with username/password login
- **Category Management**: Create reusable categories (e.g., "Toiletries", "Electronics") with items
- **Trip Creation**: Create trips by selecting categories to auto-generate packing lists
- **Template System**: Use existing trips as templates for new ones (copies categories and custom items)
- **Interactive Checklist**: Toggle items as packed with real-time progress tracking
- **Custom Items**: Add items directly to trips, with option to save them to categories for future use
- **Responsive Design**: Works on mobile and desktop with Bootstrap 5

## Tech Stack

- **Backend**: Django 6.x with Django REST Framework
- **Frontend**: Bootstrap 5, vanilla JavaScript (no SPA framework)
- **Database**: SQLite
- **Package Manager**: uv

## Development Setup

### Prerequisites

- Python 3.11+ 
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd packing-app
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Run database migrations:
   ```bash
   uv run python manage.py migrate
   ```

4. Create a superuser (optional, for admin access):
   ```bash
   uv run python manage.py createsuperuser
   ```

5. Start the development server:
   ```bash
   uv run python manage.py runserver
   ```

6. Open http://127.0.0.1:8000 in your browser

### Project Structure

```
packing-app/
├── accounts/           # User authentication app
│   ├── forms.py        # Login/registration forms
│   ├── views.py        # Auth views
│   └── urls.py
├── core/               # Main application
│   ├── api/            # REST API
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── models.py       # Category, Trip, Item models
│   ├── views.py        # Template-based views
│   ├── forms.py
│   └── urls.py
├── templates/          # HTML templates
│   ├── base.html       # Base layout with Bootstrap
│   ├── accounts/       # Auth templates
│   └── core/           # App templates
├── static/
│   ├── css/app.css     # Custom styles
│   └── js/app.js       # AJAX helpers
└── packing_project/    # Django project settings
```

### Database Schema

- **Category**: Reusable category templates belonging to a user
- **CategoryItem**: Items within a category template
- **Trip**: A specific trip with a packing checklist
- **TripCategory**: Links trips to categories (preserves category name if deleted)
- **TripItem**: Individual items in a trip's checklist (snapshot of category items + custom items)

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/categories/` | GET, POST | List/create categories |
| `/api/categories/<id>/` | GET, PUT, DELETE | Category CRUD |
| `/api/categories/<id>/items/` | GET, POST | Category items |
| `/api/categories/<id>/items/<id>/` | PUT, DELETE | Item CRUD |
| `/api/trips/` | GET, POST | List/create trips |
| `/api/trips/<id>/` | GET, PUT, DELETE | Trip CRUD |
| `/api/trips/<id>/items/` | GET, POST | Trip items |
| `/api/trips/<id>/items/<id>/` | PATCH | Toggle packed status |
| `/api/trips/<id>/items/<id>/add-to-category/` | POST | Save custom item to category |

### Running Tests

```bash
uv run python manage.py test
```

## Usage

1. **Register** a new account or login
2. **Create categories** (e.g., "Toiletries", "Clothing", "Electronics")
3. **Add items** to each category
4. **Create a trip** and select which categories to include
5. **Pack your bag** and tick off items as you go
6. **Add custom items** if you need something not in your categories
7. **Reuse trips as templates** for future similar trips
