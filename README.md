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
# or with mise
mise run test
```

### Code Quality

This project uses:
- [ruff](https://docs.astral.sh/ruff/) for Python linting/formatting
- [mypy](https://mypy.readthedocs.io/) for Python type checking
- [Biome](https://biomejs.dev/) for JavaScript/CSS linting and formatting
- [djLint](https://djlint.com/) for Django HTML template linting

```bash
# Run all checks (Python + frontend)
mise run check

# Python linting
mise run lint        # Run ruff linter
mise run format      # Format code with ruff  
mise run typecheck   # Run mypy

# Frontend linting
mise run lint:js     # Run Biome on JS/CSS
mise run lint:html   # Run djLint on HTML templates
mise run lint:frontend  # Run all frontend linters

# Auto-fix issues
mise run fix         # Fix all lint issues and format code
mise run lint:js:fix    # Fix JS/CSS issues
mise run lint:html:fix  # Fix HTML template issues
```

### Available Tasks

Run `mise tasks` to see all available commands:

| Task | Description |
|------|-------------|
| `mise run dev` | Run the development server |
| `mise run migrate` | Run database migrations |
| `mise run db` | Run makemigrations then migrate |
| `mise run test` | Run all tests |
| `mise run check` | Run all checks (lint, format, typecheck, frontend) |
| `mise run fix` | Auto-fix lint and format issues |
| `mise run lint:frontend` | Run frontend linters (JS, CSS, HTML) |
| `mise run shell` | Open Django shell |
| `mise run setup` | Initial project setup |

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

### Nginx Reverse Proxy

The Docker container is designed to run behind nginx with SSL termination. Example nginx configuration:

```nginx
server {
    listen 443 ssl http2;
    server_name myapp.example.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name myapp.example.com;
    return 301 https://$server_name$request_uri;
}
```

### CI/CD Pipeline

The project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that:

1. **On every push/PR to main:**
   - Runs Python linting (ruff) and type checking (mypy)
   - Runs frontend linting (Biome for JS/CSS, djLint for HTML)
   - Runs Django tests

2. **On push to main (after tests pass):**
   - Builds a Docker image
   - Pushes to `ghcr.io/<owner>/packing-app:latest`

To use it:

1. Ensure your repository has GitHub Packages enabled
2. The workflow uses `GITHUB_TOKEN` automatically (no secrets needed)
3. After the first successful build, the image will be available at `ghcr.io/<owner>/packing-app:latest`

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
