# QBox Backend (Django)

A Django-based backend API for the QBox application.  
This project provides REST APIs, JWT authentication, and Swagger documentation for all endpoints.  

---

## Table of Contents

- [Features](#features)  
- [Tech Stack](#tech-stack)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [Environment Variables](#environment-variables)  
- [Database Setup](#database-setup)  
- [Running the Project](#running-the-project)  
- [API Documentation](#api-documentation)  
- [Testing](#testing)  
- [Deployment](#deployment)  
- [Git Workflow](#git-workflow)  
- [Best Practices](#best-practices)  
- [License](#license)  

---

## Features

- RESTful API endpoints using Django REST Framework  
- Swagger API documentation (drf-yasg)  
- JWT / token-based authentication  
- PostgreSQL database integration  
- Isolated virtual environment setup  
- Example CRUD endpoints for `driver` and other models  

---

## Tech Stack

- **Backend:** Python 3.11+, Django 6.x, Django REST Framework  
- **Database:** PostgreSQL 14+  
- **API Docs:** drf-yasg / Swagger  
- **Server (production):** Gunicorn + Nginx  
- **Dev Tools:** virtualenv, pip, Git, ngrok  

---

## Prerequisites

Make sure the following are installed:

- Python 3.11+  
- pip or pipenv  
- PostgreSQL 14+  
- Git  
- virtualenv (recommended)  

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Hegmon/Qbox-backend/
cd Qbox-backend


Create and activate a virtual environment:
# Linux / Mac
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1


Upgrade pip (optional but recommended):
pip install --upgrade pip

Install all required packages:
pip install -r requirements.txt

Verify installation:
python -m django --version
python -m pip list

