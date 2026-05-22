# JobPlatform — Дипломный проект

Платформа для поиска работы с фокусом на справедливые требования для Junior-разработчиков и стажёров.

## Архитектура

- **Backend**: Django 4.2 + Django REST Framework (REST API + JWT)
- **Frontend**: Flutter (кроссплатформенное мобильное приложение)
- **Database**: PostgreSQL (SQLite для локальной разработки)

## Быстрый старт

```bash
# Backend
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver

# Frontend (в отдельном терминале)
cd frontend_app
flutter pub get
flutter run
```

Подробные инструкции: [SETUP.md](SETUP.md)

## Структура проекта

```
diploma_project/
├── backend/                     # Django REST API
│   ├── accounts/                # Пользователи, профили, авторизация (JWT)
│   ├── jobs/                    # Вакансии, фильтрация, избранное
│   ├── applications/            # Отклики, статусы, чат
│   ├── tests_system/            # Тесты навыков
│   ├── analytics/               # Анализ вакансий, матчинг, сравнение
│   ├── reviews/                 # Отзывы о компаниях
│   ├── notifications/           # Уведомления
│   ├── config/                  # Настройки, URLs, management commands
│   ├── templates/               # HTML-шаблоны веб-интерфейса
│   └── requirements.txt
├── frontend_app/                # Flutter мобильное приложение
│   ├── lib/
│   │   ├── main.dart
│   │   ├── screens/             # 13 экранов приложения
│   │   ├── services/            # API-клиент, тема
│   │   ├── widgets/             # Общие виджеты
│   │   └── l10n/                # Локализация
│   └── pubspec.yaml
├── docker-compose.yml
├── Dockerfile
├── SETUP.md                     # Инструкция по установке
├── IDEA.md                      # Концепция проекта
└── PROJECT_INFO.md              # Техническое описание
```

## Документация

| Файл | Содержание |
|------|------------|
| [SETUP.md](SETUP.md) | Установка, запуск, тестовые данные |
| [IDEA.md](IDEA.md) | Идея и концепция проекта |
| [PROJECT_INFO.md](PROJECT_INFO.md) | Модули, функциональность, стек |
| [CLAUDE.md](CLAUDE.md) | Инструкции для Claude Code |

## API

После запуска backend доступны:
- Swagger UI: http://127.0.0.1:8000/api/docs/
- ReDoc: http://127.0.0.1:8000/api/redoc/
- Admin: http://127.0.0.1:8000/admin/
