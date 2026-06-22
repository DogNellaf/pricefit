# PriceFit

> 🇬🇧 English | [🇷🇺 Русский](README.ru.md)

A Django web application for generating target-group recommendations based on price-range matching. Users create price-range requests; the system computes a Jaccard correlation coefficient for each target group and ranks results automatically.

## Features

- **User accounts** — registration, login, logout via Django built-in auth
- **Requests** — create, view, edit and delete price-range queries
- **Target groups** — staff-managed catalog of groups with optional budget ranges
- **Automated analysis** — one-click Jaccard coefficient computation for every group
- **Admin panel** — full Django admin interface for data management
- **Responsive UI** — Bootstrap 5 interface with progress-bar coefficient visualisation

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 3.2 |
| Database | SQLite (development) |
| Frontend | Bootstrap 5 (CDN) |
| Language | Python 3.8+ |

## Requirements

- Python 3.8+
- pip

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd Программа

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create a superuser (required to manage target groups)
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`.

## Usage

1. Register a user account or log in.
2. Navigate to **Target Groups** and ask a staff member (or use the admin panel) to add groups with budget ranges.
3. Go to **My Requests → New Request** and enter your price range.
4. Open the request and click **Run Analysis** — the system computes a coefficient (0–1) for each target group. Higher values indicate better price-range overlap.

### Coefficient interpretation

| Range | Meaning |
|---|---|
| 0.7 – 1.0 | Strong match |
| 0.3 – 0.7 | Partial match |
| 0.0 – 0.3 | Weak or no match |

## Environment Variables

For production deployments, set these environment variables instead of using defaults:

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | insecure dev key |
| `DEBUG` | Enable debug mode (`True`/`False`) | `True` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | _(empty)_ |

## URL Routes

| Method | URL | Description |
|---|---|---|
| GET | `/` | Home / dashboard |
| GET/POST | `/accounts/register/` | Register new user |
| GET/POST | `/accounts/login/` | Log in |
| POST | `/accounts/logout/` | Log out |
| GET | `/requests/` | List user's requests |
| GET/POST | `/requests/new/` | Create a new request |
| GET | `/requests/<id>/` | Request detail with recommendations |
| GET/POST | `/requests/<id>/edit/` | Edit a request |
| POST | `/requests/<id>/delete/` | Delete a request |
| POST | `/requests/<id>/analyze/` | Run recommendation analysis |
| GET | `/groups/` | List target groups (public) |
| GET/POST | `/groups/new/` | Create group (staff only) |
| GET/POST | `/groups/<id>/edit/` | Edit group (staff only) |
| POST | `/groups/<id>/delete/` | Delete group (staff only) |
| GET | `/admin/` | Django admin panel |

## Running Tests

```bash
python manage.py test main
```

The test suite covers models, services, forms and views (including authentication and permission checks).

## Project Structure

```
Программа/
├── prog/                  # Django project configuration
│   ├── settings.py
│   └── urls.py
├── main/                  # Application
│   ├── models.py          # TargetGroup, Request, Analysis
│   ├── views.py           # All view functions
│   ├── forms.py           # RequestForm, TargetGroupForm
│   ├── services.py        # Recommendation algorithm
│   ├── admin.py           # Admin registrations
│   ├── urls.py            # URL patterns
│   ├── tests.py           # Test suite
│   ├── migrations/
│   └── templates/
│       ├── main/          # Application templates
│       └── registration/  # Auth templates
├── requirements.txt
└── manage.py
```

## License

[MIT](LICENSE)
