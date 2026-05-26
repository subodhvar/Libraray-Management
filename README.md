# Neighborhood Library Service (Django + DRF)

This project implements the take-home requirements using:
- **Backend API:** Django REST Framework (REST)
- **Database:** PostgreSQL (primary target)
- **Frontend:** Django Templates (server-rendered UI, no React)

## Features

- Create/update/list books
- Create/update/list members
- Borrow a book for a member
- Return a borrowed book
- List current borrowed books by member
- Basic validation for unavailable books and inactive members

## Database Schema

### `library_book`
- `id` (PK)
- `title`
- `author`
- `isbn` (unique)
- `published_year` (nullable)
- `total_copies`
- `available_copies`
- `created_at`, `updated_at`

### `library_member`
- `id` (PK)
- `full_name`
- `email` (unique)
- `phone`
- `address`
- `is_active`
- `created_at`, `updated_at`

### `library_loan`
- `id` (PK)
- `book_id` (FK -> `library_book.id`)
- `member_id` (FK -> `library_member.id`)
- `borrowed_at`
- `due_date`
- `returned_at` (nullable)
- `notes`
- `created_at`, `updated_at`

## Project Structure

- `config/` Django project settings/urls
- `library/` app (models, serializers, views, urls, tests)
- `templates/` Django frontend templates
- `docker-compose.yml` PostgreSQL container
- `.env.example` environment variables template

## Setup

1. Copy `.env.example` to `.env`.
2. Install dependencies.
3. Start PostgreSQL.
4. Run migrations.
5. Start server.

### 1) Create `.env`

Use `.env.example` as reference. For your local setup, set:
- `DB_ENGINE=postgres`
- `POSTGRES_HOST=localhost`
- `POSTGRES_PORT=5432`
- `POSTGRES_DB=library`
- `POSTGRES_USER=postgres` (or your local PostgreSQL user)
- `POSTGRES_PASSWORD=` (set if your user requires a password)

### 2) Install dependencies

```powershell
Set-Location "C:\Users\subodh\Downloads\Library_service"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3) PostgreSQL

If you already have local PostgreSQL running on `localhost:5432` with database `library`, skip Docker.

Optional Docker alternative:

```powershell
Set-Location "C:\Users\subodh\Downloads\Library_service"
docker compose up -d
```

### 4) Run migrations

```powershell
Set-Location "C:\Users\subodh\Downloads\Library_service"
.\.venv\Scripts\python.exe manage.py migrate
```

### 5) Run server

```powershell
Set-Location "C:\Users\subodh\Downloads\Library_service"
.\.venv\Scripts\python.exe manage.py runserver
```

Frontend and API root:
- UI: http://127.0.0.1:8000/
- API: http://127.0.0.1:8000/api/

Frontend edit pages:
- `GET /books/{id}/edit/`
- `GET /members/{id}/edit/`

## API Endpoints

### Books
- `GET /api/books/`
- `POST /api/books/`
- `PUT/PATCH /api/books/{id}/`
- `POST /api/books/{id}/borrow/`
- `POST /api/books/{id}/return/`

### Members
- `GET /api/members/`
- `POST /api/members/`
- `PUT/PATCH /api/members/{id}/`
- `GET /api/members/{id}/borrowed-books/`

### Loans
- `GET /api/loans/`
- `GET /api/loans/?active=true`
- `GET /api/loans/?member_id={member_id}`

## Sample API Calls

### Borrow a book

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/books/1/borrow/" -ContentType "application/json" -Body '{"member_id":1,"due_date":"2026-12-31","notes":"Handle with care"}'
```

### Return a book

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/books/1/return/" -ContentType "application/json" -Body '{"loan_id":1}'
```

## Test

```powershell
Set-Location "C:\Users\subodh\Downloads\Library_service"
$env:DB_ENGINE='sqlite'
.\.venv\Scripts\python.exe manage.py test
```

`DB_ENGINE=sqlite` is used in tests for lightweight local execution. For normal app usage, keep `DB_ENGINE=postgres`.

