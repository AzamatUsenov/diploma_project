# CLAUDE.md — Job Platform (Дипломный проект)

Этот файл содержит инструкции для Claude Code при работе над дипломным проектом.

## 📋 Описание проекта

**Job Platform** — веб-приложение для поиска работы с фокусом на справедливые требования для джуниоров и стажировок.

- **Тип**: Django REST API + (будущий) фронтенд
- **Цель**: Решить проблему завышенных требований на Junior вакансиях
- **Целевая аудитория**: Компании и соискатели (особенно джуниоры)

## 🏗️ Архитектура проекта

```
diploma_project/
├── backend/                    # Django приложение
│   ├── accounts/               # Аутентификация, профили пользователей
│   ├── applications/           # Заявки на вакансии
│   ├── jobs/                   # Управление вакансиями (TODO)
│   ├── reviews/                # Отзывы о компаниях (TODO)
│   ├── manage.py               # Django CLI
│   ├── requirements.txt         # Python зависимости
│   └── settings.py             # Django конфиг
├── docker-compose.yml          # Local dev environment
├── Dockerfile                  # Production image
├── IDEA.md                      # Описание идеи проекта
├── PROJECT_INFO.md             # Спецификация требований
└── README.md                    # Getting started
```

## 🔧 Требования для разработки

### Перед началом
1. Python 3.9+
2. Django 4.x
3. PostgreSQL (в Docker или локально)
4. Virtual environment активирован

### Установка зависимостей
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Docker
```bash
docker-compose up -d  # Запустить БД и кэш
cd backend && python manage.py migrate
python manage.py runserver
```

## 📝 Git Commit Rules

**ВАЖНО**: Создавайте отдельные коммиты для каждого файла (не бундлируйте).

Примеры:
- `git add accounts/models.py` → commit с описанием изменений models.py
- `git add accounts/views.py` → отдельный commit
- `git add accounts/tests.py` → отдельный commit

Это делает историю чистой и облегчает revert/cherry-pick.

## 🎯 Workflow разработки

### 1. Планирование (Plan Mode)
Используй `/plan` для сложных задач:
- Архитектурные решения
- Новые модули/приложения
- Рефакторинг существующего кода

### 2. Реализация
- Начни с моделей (models.py)
- Затем views/serializers
- Добавь тесты параллельно
- Коммить часто (минимум один в час)

### 3. Тестирование
```bash
python manage.py test                    # Все тесты
python manage.py test accounts           # Тесты модуля
coverage run --source='.' manage.py test
coverage report
```

### 4. Code Review
- Перед PR запусти: `python manage.py check`
- Проверь coverage в test_coverage.md
- Используй `/code-review` для анализа PR

## 💡 Django Best Practices (для этого проекта)

### Модели
- Используй abstract base models для общей функциональности
- Всегда добавляй `created_at`, `updated_at` полями (с auto_now/auto_now_add)
- Переопредели `__str__` для всех моделей

### Views & Serializers
- Используй ViewSets + Routers для CRUD
- Добавляй permission classes для auth
- Документируй API с docstrings

### Тесты
- Пиши тесты для каждого API endpoint
- Используй TestCase с setUp/tearDown
- Минимум 80% code coverage

## 🔐 Безопасность

- ❌ Не коммить `.env` файлы (используй `.env.example`)
- ✅ Используй Django security middleware
- ✅ Валидируй все входные данные
- ✅ Используй CSRF protection

## 📚 Основные модули

### accounts
- User модель (расширяемая)
- Authentication endpoints
- Profile management

### applications
- Job application модель
- Application workflow
- Notifications (TODO)

### jobs (TODO)
- Job posting
- Filtering by level (Junior/Mid/Senior)
- Requirements management

### reviews (TODO)
- Company reviews
- Rating system
- Moderation

## 🚀 Когда вызывать Claude

Используй Claude для:
- ✅ Написания/рефакторинга кода
- ✅ Отладки ошибок (приложи traceback или скриншот)
- ✅ Планирования архитектуры
- ✅ Написания тестов
- ✅ Оптимизации запросов

Не забывай:
- Пастить error messages полностью
- Приложить релевантный код контекст
- Описать что ты пытался сделать

## 📋 Useful Commands

```bash
# Development
python manage.py runserver
python manage.py shell

# Database
python manage.py makemigrations
python manage.py migrate
python manage.py dbshell

# Testing
python manage.py test
coverage run --source='.' manage.py test
coverage report -m

# Admin
python manage.py createsuperuser
python manage.py changepassword <username>
```

## 🎓 Reference Materials

- [Claude Code Best Practices](../claude-code-best-practice/) — общие рекомендации
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- PROJECT_INFO.md — требования проекта
- test_coverage.md — текущее состояние тестов

---

**Last Updated**: 2026-04-12
