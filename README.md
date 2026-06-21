# PriceFit

> [Русская версия](README.ru.md)

A Django web application for generating target-group recommendations based on price-range matching. Users create price-range requests; the system computes a Jaccard correlation coefficient for each target group and ranks results automatically.

---

## Features

- **User accounts** — registration, login, logout via Django built-in auth
- **Requests** — create, view, edit and delete price-range queries
- **Target groups** — staff-managed catalog of groups with optional budget ranges
- **Automated analysis** — one-click Jaccard coefficient computation for every group
- **Admin panel** — full Django admin interface for data management
- **Responsive UI** — Bootstrap 5 interface with progress-bar coefficient visualisation

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 3.2 |
| Database | SQLite (development) |
| Frontend | Bootstrap 5 (CDN) |
| Language | Python 3.8+ |

---

## Installation

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd Программа
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** (required to manage target groups)

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**

   ```bash
   python manage.py runserver
   ```

   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## Usage

1. Register a user account or log in.
2. Navigate to **Target Groups** and ask a staff member (or use the admin panel) to add groups with budget ranges.
3. Go to **My Requests → New Request** and enter your price range.
4. Open the request and click **Run Analysis** — the system computes a coefficient (0–1) for each target group. Higher values indicate better price-range overlap.

### Coefficient interpretation

| Range | Meaning |
|-------|---------|
| 0.7 – 1.0 | Strong match |
| 0.3 – 0.7 | Partial match |
| 0.0 – 0.3 | Weak or no match |

---

## URL Routes

| Method | URL | Description |
|--------|-----|-------------|
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

---

## Running Tests

```bash
python manage.py test main
```

The test suite covers models, services, forms and views (including authentication and permission checks).

---

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

---

## License

[MIT](LICENSE)
