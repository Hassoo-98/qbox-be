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
- Environment variable configuration (`.env`)
- Example CRUD operations (Driver model & more)
- Production deployment hints (Gunicorn + Nginx)
- Modern project structure & best practices
- Virtual environment setup

---

## 🛠 Tech Stack

| Category              | Technology                        | Version    |
|-----------------------|-----------------------------------|------------|
| Language              | Python                            | 3.11+      |
| Web Framework         | Django                            | 6.x        |
| API Framework         | Django REST Framework             | latest     |
| Authentication        | djangorestframework-simplejwt     | latest     |
| API Documentation     | drf-yasg (Swagger + Redoc)        | latest     |
| Database              | PostgreSQL                        | 14+        |
| Production Server     | Gunicorn + Nginx                  | —          |
| Dependency Management | pip / requirements.txt            | —          |

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
# 1. Clone the repository
git clone https://github.com/Hegmon/Qbox-backend.git
cd Qbox-backend

# 2. Create and activate virtual environment

# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate.bat

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Create .env file from example (if exists) or manually
#    (see Environment Variables section below)
cp .env.example .env    # only if you have .env.example

# 5. Apply database migrations
python manage.py makemigrations
python manage.py migrate

# 6. (Optional) Create a superuser
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
