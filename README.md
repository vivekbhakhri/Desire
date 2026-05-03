# Desire

E-commerce site that lets local sellers list products and customers buy from home.

## Requirements

- Python 3.11+ (developed against 3.14)
- Django 5.x (see `requirements.txt`)

## Local setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv virtual-Env
source virtual-Env/bin/activate           # macOS / Linux
# .\virtual-Env\Scripts\activate          # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# edit .env and set SECRET_KEY plus any payment / email credentials you need

# 4. Apply migrations and start the dev server
python manage.py migrate
python manage.py runserver
```

The site will be available at <http://127.0.0.1:8000/>.

## Configuration

All secrets are loaded from environment variables via `python-decouple`. See
[`.env.example`](./.env.example) for the full list. Production deployments
should set `ENVIRONMENT=production`, `DEBUG=False`, and a real `SECRET_KEY`.

## Notes

- `instamojo_wrapper` is unmaintained and has no Python 3.10+ wheels. The
  InstaMojo integration is loaded lazily and the rest of the app runs without
  it. Razorpay is the recommended payment gateway.
- The `demo/azure.py` settings module is for Azure App Service deployments
  (Postgres + Azure blob storage). Activate with
  `DJANGO_SETTINGS_MODULE=demo.azure`.
