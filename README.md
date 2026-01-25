# Packing App

⚠️ 🤖 - Heavily AI assisted project

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
- **Package Manager**: uv (Python), pnpm (JavaScript)

## Development Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- [mise](https://mise.jdx.dev/) (optional, for running common tasks)
- Node.js (LTS) and [pnpm](https://pnpm.io/) (for frontend linting)

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd packing-app
   ```

2. Install dependencies:

   ```bash
   uv sync
   pnpm install
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

6. Open <http://127.0.0.1:8000> in your browser

### Project Structure

- **accounts/**: User authentication (login, logout, registration)
- **core/**: Main application with models, views, and forms
- **core/api/**: REST API using Django REST Framework
- **templates/**: HTML templates extending `base.html`
- **static/**: CSS and JavaScript assets
- **packing_project/**: Django project settings

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
# or with mise
mise run test
```

### Code Quality

This project uses ruff, mypy, Biome, and djLint for linting and formatting. Run `mise tasks` to see all available commands, or see `mise.toml` for details.

Essential commands:

```bash
mise run dev     # Run development server
mise run check   # Run all checks (lint, format, typecheck) - run before committing
mise run fix     # Auto-fix lint and format issues
mise run test    # Run all tests
mise run db      # Run makemigrations + migrate
```

## Usage

1. **Register** a new account or login
2. **Create categories** (e.g., "Toiletries", "Clothing", "Electronics")
3. **Add items** to each category
4. **Create a trip** and select which categories to include
5. **Pack your bag** and tick off items as you go
6. **Add custom items** if you need something not in your categories
7. **Reuse trips as templates** for future similar trips

## Deployment

### Docker Quick Start

1. Create a `docker-compose.yaml` file (or copy the example from the repo):

   ```yaml
   services:
     web:
       image: ghcr.io/OWNER/packing-app:latest
       ports:
         - "8000:8000"
       environment:
         - SECRET_KEY=your-secret-key-here
         - DEBUG=False
         - ALLOWED_HOSTS=localhost,myapp.example.com
         - CSRF_TRUSTED_ORIGINS=https://myapp.example.com
       volumes:
         - sqlite_data:/app/data
       restart: unless-stopped

   volumes:
     sqlite_data:
   ```

2. Generate a secure secret key:

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```

3. Start the application:

   ```bash
   docker compose up -d
   ```

4. View auto-generated superuser credentials:

   ```bash
   docker compose logs web
   ```

   On first run, if you don't provide `DJANGO_SUPERUSER_*` environment variables,
   credentials will be auto-generated and printed to the logs.

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | **Yes** (prod) | Insecure dev key | Django secret key. Generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | No | `False` | Enable debug mode. Never use `True` in production |
| `ALLOWED_HOSTS` | No | `localhost` | Comma-separated list of allowed hostnames |
| `CSRF_TRUSTED_ORIGINS` | **Yes** (HTTPS) | Empty | Comma-separated origins with scheme, e.g., `https://myapp.example.com` |
| `SECURE_COOKIES` | No | `True` | Set cookies as secure (HTTPS only). Set to `False` for local HTTP testing |
| `DJANGO_SUPERUSER_USERNAME` | No | `admin` | Superuser username (auto-generated if not set) |
| `DJANGO_SUPERUSER_PASSWORD` | No | Auto-generated | Superuser password (printed to logs if auto-generated) |
| `DJANGO_SUPERUSER_EMAIL` | No | `admin@example.com` | Superuser email |

### CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs linting and tests on every push/PR to main. On successful pushes to main, it builds and pushes a Docker image to `ghcr.io/<owner>/packing-app:latest`.

### Building Locally

```bash
# Build the Docker image
docker build -t packing-app .

# Run locally
docker run -p 8000:8000 \
  -e SECRET_KEY=dev-secret-key \
  -e DEBUG=False \
  -e ALLOWED_HOSTS=localhost \
  -e SECURE_COOKIES=False \
  -v packing_data:/app/data \
  packing-app
```
