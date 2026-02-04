# QBox Backend

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-6.x-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/django--rest--framework-3.x-ff69b4.svg)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-14+-336791.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**QBox Backend** — production-ready REST API powering the QBox application.

Secure JWT authentication • Comprehensive Swagger documentation • Clean CRUD endpoints • PostgreSQL integration

---

## ✨ Features

- RESTful API built with **Django REST Framework**
- JWT authentication (Simple JWT)
- Interactive API documentation via **Swagger UI** + **Redoc**
- PostgreSQL database with proper migrations
- Environment variable configuration (.env)
- Example CRUD operations (Driver model & more)
- Production deployment hints (Gunicorn + Nginx)
- Modern project structure & best practices
- Virtual environment setup

---

## 🛠 Tech Stack

| Category            | Technology                        | Version    |
|---------------------|-----------------------------------|------------|
| Language            | Python                            | 3.11+      |
| Web Framework       | Django                            | 6.x        |
| API Framework       | Django REST Framework             | latest     |
| Authentication      | djangorestframework-simplejwt     | latest     |
| API Documentation   | drf-yasg (Swagger + Redoc)        | latest     |
| Database            | PostgreSQL                        | 14+        |
| Production Server   | Gunicorn + Nginx                  | —          |
| Dependency Management | pip / requirements.txt          | —          |

---

## 📋 Prerequisites

- Python ≥ 3.11
- pip
- PostgreSQL ≥ 14
- Git
- virtualenv / venv (recommended)

---

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/Hegmon/Qbox-backend.git
cd Qbox-backend

# 2. Create & activate virtual environment
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows (cmd)
python -m venv venv
venv\Scripts\activate.bat

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Create .env file (example below)
cp .env.example .env    # if you have .env.example
# or manually create .env and fill values

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. (optional) Create superuser
python manage.py createsuperuser

# 7. Start development server
python manage.py runserver
Open: http://127.0.0.1:8000/
API Documentation:
→ http://127.0.0.1:8000/swagger/
→ http://127.0.0.1:8000/redoc/

⚙️ Environment Variables (.env)
env# === Django ===
SECRET_KEY=your-very-long-random-secure-key-here
DEBUG=True               # change to False in production!
ALLOWED_HOSTS=localhost,127.0.0.1

# === Database (PostgreSQL) ===
DB_NAME=qbox_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# === JWT settings (optional customization) ===
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7
Tip: Never commit .env to git — add it to .gitignore

🗄 Database Setup
Bash# Create database (one-time)
createdb -U postgres qbox_db
# or use pgAdmin / other client

# Apply migrations
python manage.py makemigrations
python manage.py migrate

📚 API Documentation
Automatically generated:

Interactive Swagger UI → /swagger/
Clean Redoc view → /redoc/

Authentication method: Bearer Token (JWT)
Example:
textAuthorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

🧪 Running Tests
Bashpython manage.py test
# or more detailed output:
python manage.py test --verbosity=2
