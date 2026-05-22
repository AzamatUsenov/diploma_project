# CLAUDE.md — JobPlatform (Дипломный проект)

Инструкции для Claude Code при работе над проектом.

## Описание проекта

**JobPlatform** — платформа для поиска работы с фокусом на справедливые требования для Junior-разработчиков.

- **Backend**: Django 4.2 + DRF 3.14 (REST API, JWT-авторизация)
- **Frontend**: Flutter 3.9+ (мобильное кроссплатформенное приложение)
- **Database**: PostgreSQL 14+ (SQLite для dev)

## Архитектура

```
diploma_project/
├── backend/                     # Django REST API
│   ├── accounts/                # Пользователи, профили, JWT-авторизация, резюме
│   ├── jobs/                    # Вакансии, фильтрация, избранное
│   ├── applications/            # Отклики, статусы, чат (сообщения)
│   ├── tests_system/            # Тесты навыков, вопросы, результаты
│   ├── analytics/               # Анализ вакансий, матчинг, сравнение, рекомендации
│   ├── reviews/                 # Отзывы о компаниях
│   ├── notifications/           # Уведомления (сигналы)
│   ├── config/                  # settings, urls, management commands (seed_data)
│   ├── templates/               # HTML-шаблоны веб-интерфейса
│   ├── requirements.txt
│   └── manage.py
├── frontend_app/                # Flutter приложение
│   ├── lib/
│   │   ├── main.dart            # Точка входа, навигация, JWT-проверка
│   │   ├── screens/             # 13 экранов
│   │   ├── services/            # api_service.dart, theme_service.dart
│   │   ├── widgets/             # common.dart (SkillChip, LevelBadge и др.)
│   │   └── l10n/                # Локализация (русский)
│   └── pubspec.yaml
├── docker-compose.yml
├── Dockerfile
└── SETUP.md                     # Инструкция по установке и запуску
```

## Запуск

```bash
# Backend
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data       # Тестовые данные
python manage.py runserver

# Frontend
cd frontend_app
flutter pub get
flutter run
```

## Git Commit Rules

**ВАЖНО**: Создавайте отдельные коммиты для каждого файла (не бундлируйте).

```bash
git add accounts/models.py && git commit -m "..."
git add accounts/views.py && git commit -m "..."
```

## Тестирование

```bash
cd backend
python manage.py test                    # Все тесты
python manage.py test accounts           # Один модуль
python manage.py test accounts.tests.TestClassName.test_method  # Один тест
```

## Полезные команды

```bash
# Backend
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data          # Загрузить демо-данные
python manage.py seed_data --reset  # Сбросить + загрузить
python manage.py createsuperuser

# Frontend
cd frontend_app
flutter pub get
flutter run
flutter analyze
```

## API Endpoints (основные)

```
POST /api/accounts/register/
POST /api/accounts/login/
POST /api/accounts/token/refresh/
GET  /api/accounts/profiles/me/

GET/POST    /api/jobs/
GET         /api/jobs/{id}/
POST        /api/jobs/{id}/favorite/

GET/POST    /api/applications/
PATCH       /api/applications/{id}/status/
GET         /api/applications/{id}/messages/
POST        /api/applications/{id}/send/

GET         /api/tests/
POST        /api/tests/{id}/submit/

GET         /api/analytics/analyze/{job_id}/
POST        /api/analytics/match/
POST        /api/analytics/compare/

GET/POST    /api/reviews/
GET/POST    /api/notifications/
```

## Conventions

- ViewSets + Routers для CRUD
- Permission classes для разграничения HR / applicant
- Serializers для валидации
- Signals для уведомлений (notifications/signals.py)
- `created_at` / `updated_at` на всех моделях

---

**Last Updated**: 2026-05-22
