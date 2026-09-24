# Sarvotam Furniture

A Django furniture discovery, showroom enquiry, and web analytics demonstration for Sarvotam Furniture, Yamunanagar.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_store
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

The seed command creates 900 catalogue products, 56 categories, and a development admin account:

- Username: `demo-admin`
- Password: `SarvotamDemo2026!`

Change this password before using the project beyond local demonstration. No production credentials are included.

## Main routes

- `/` homepage
- `/products/` paginated catalogue and search
- `/category/<slug>/` category catalogue
- `/product/<slug>/` product detail
- `/cart/`, `/wishlist/`, `/enquiry/`, `/showroom/`
- `/register/`, `/accounts/login/`, `/account/`
- `/admin/` Django administration
- `/admin/analytics/` demo analytics dashboard

## Notes

The product catalogue uses seeded, replaceable image URLs and realistic generated furniture attributes. Cart and wishlist are session-backed for this demonstration. Enquiries and analytics events are stored in SQLite. Online payments are intentionally not implemented: customers shortlist online and complete selection and payment at the physical showroom.

Analytics uses the provider-neutral `AnalyticsEvent` model and `/api/analytics/events/` endpoint. Events include page views, product views, searches, cart actions, wishlist actions, enquiry starts/submissions, registration, and showroom requests.
