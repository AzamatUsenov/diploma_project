# Junior Jobs - Django Backend

Job board platform for junior developers and HR managers to connect, with built-in skill testing.

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- pip

### Installation

1. **Clone and navigate to backend:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create .env file:**
```bash
cp .env.example .env
```

5. **Run migrations:**
```bash
python manage.py migrate
```

6. **Create superuser:**
```bash
python manage.py createsuperuser
```

7. **Run development server:**
```bash
python manage.py runserver
```

Server will be available at `http://localhost:8000`

### With Docker

1. **Build and run:**
```bash
docker-compose up --build
```

2. **Run migrations in container:**
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Project Structure

```
backend/
├── config/              # Django settings
├── accounts/            # User authentication & profiles
├── jobs/                # Job postings
├── applications/        # Job applications
├── tests_system/        # Skill testing system
├── templates/           # HTML templates
├── static/              # Static files
├── manage.py
└── requirements.txt
```

## Features

- **User Registration & Roles** (Junior/HR)
- **Job Posting** with junior-friendly flags
- **Job Applications** with status tracking
- **Skill Tests** (Quiz + Code challenges)
- **Test Results** with scoring
- **Profile Management**

## Admin Panel

Access at `/admin` with superuser credentials

## API Endpoints

- `/api/accounts/register/` - Register new user
- `/api/accounts/login/` - User login
- `/api/accounts/profile/` - User profile
- `/api/jobs/` - List/create jobs
- `/api/jobs/<id>/` - Job detail
- `/api/applications/` - User applications
- `/api/applications/apply/<job_id>/` - Apply to job
- `/api/tests/` - Skill tests
- `/api/tests/<id>/take/` - Take test

## Database Models

### User
- UserProfile: Role, company info, portfolio links

### Jobs
- Job: Title, description, junior-friendly flags
- JobTag: Tech skills tags

### Applications
- Application: Job application with status

### Tests
- SkillTest: Test metadata
- Question: Quiz questions or code challenges
- TestResult: User test results
- Answer: Individual answers

## Development

Run tests:
```bash
python manage.py test
```

Create migrations after model changes:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Notes

- All timestamps are in UTC
- Database: PostgreSQL (configured in settings.py)
- Static/Media files served through Django in DEBUG mode
