# JobPlatform — Инструкция по установке и запуску

## Требования

| Компонент | Версия |
|---|---|
| Python | 3.9+ |
| PostgreSQL | 14+ |
| Flutter | 3.9+ (Dart SDK ^3.9.2) |
| Git | любая актуальная |

---

## 1. Клонирование репозитория

```bash
git clone <url-репозитория>
cd diploma_project
```

---

## 2. Backend (Django REST API)

### 2.1 Виртуальное окружение

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 2.2 Установка зависимостей Python

```bash
pip install -r requirements.txt
```

Основные пакеты:
- Django 4.2
- Django REST Framework 3.14
- djangorestframework-simplejwt (JWT-аутентификация)
- psycopg2-binary (PostgreSQL драйвер)
- django-cors-headers (CORS для фронтенда)
- django-filter (фильтрация API)
- drf-spectacular (OpenAPI документация)
- python-decouple (переменные окружения)
- Pillow (работа с изображениями)
- gunicorn (WSGI-сервер для продакшна)

### 2.3 Настройка базы данных PostgreSQL

Создайте базу данных:

```sql
-- В psql или pgAdmin:
CREATE DATABASE jobplatform;
```

Создайте файл `backend/.env`:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=jobplatform
DB_USER=postgres
DB_PASSWORD=<ваш_пароль>
DB_HOST=localhost
DB_PORT=5432
```

> Без `.env` файла Django будет использовать SQLite (`db.sqlite3`).

### 2.4 Применение миграций

```bash
python manage.py migrate
```

### 2.5 Создание суперпользователя (админка)

```bash
python manage.py createsuperuser
```

### 2.6 Загрузка тестовых данных

```bash
python manage.py seed_data
```

Это создаст:
- **15 пользователей** (12 соискателей + 3 HR-менеджера)
- **20 вакансий** (12 от TechCorp, 4 от StartupX, 4 от DataFlow)
- **10 тестов** с 86 вопросами (Python, JavaScript, Django, React, SQL, Git, Java, Docker)
- **26 откликов** на вакансии
- **28 избранных** вакансий

Тестовые учётки (пароль для всех: `password123`):

| Логин | Роль | Описание |
|---|---|---|
| `hr_techcorp` | HR | TechCorp Kazakhstan, 12 вакансий |
| `hr_startupx` | HR | StartupX, 4 вакансии |
| `hr_dataflow` | HR | DataFlow Analytics, 4 вакансии |
| `alice` | Соискатель | Junior Python |
| `bob` | Соискатель | Junior Frontend React |
| `charlie` | Соискатель | Middle Fullstack |
| `erik` | Соискатель | Senior Backend |

> Полный сброс и повторная загрузка: `python manage.py seed_data --reset`

### 2.7 Запуск сервера

```bash
python manage.py runserver
```

Доступные URL:
- API: http://127.0.0.1:8000/api/
- Админка: http://127.0.0.1:8000/admin/
- Swagger: http://127.0.0.1:8000/api/docs/
- ReDoc: http://127.0.0.1:8000/api/redoc/
- Веб-интерфейс: http://127.0.0.1:8000/

---

## 3. Frontend (Flutter-приложение)

### 3.1 Установка Flutter SDK

Скачайте и установите Flutter: https://docs.flutter.dev/get-started/install

Проверьте установку:

```bash
flutter doctor
```

### 3.2 Установка зависимостей

```bash
cd frontend_app
flutter pub get
```

Основные пакеты:
- http (HTTP-клиент)
- shared_preferences (локальное хранилище токенов)
- intl (интернационализация)

### 3.3 Настройка API URL

Файл `frontend_app/lib/services/api_service.dart`, строка 6:

```dart
static const String baseUrl = 'http://127.0.0.1:8000/api';
```

Измените адрес в зависимости от платформы:

| Платформа | URL |
|---|---|
| Windows/macOS/Web | `http://127.0.0.1:8000/api` |
| Android эмулятор | `http://10.0.2.2:8000/api` |
| Физическое устройство | `http://<IP-компьютера>:8000/api` |

### 3.4 Запуск приложения

```bash
flutter run
```

Выберите платформу (Windows, Chrome, Edge или подключённое устройство).

---

## 4. Запуск через Docker (альтернатива)

Если не хотите устанавливать PostgreSQL локально:

```bash
# Из корня проекта
docker-compose up -d
```

Это поднимет PostgreSQL + Django-сервер. После этого:

```bash
cd backend
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser
```

---

## 5. Структура проекта

```
diploma_project/
├── backend/                     # Django REST API
│   ├── accounts/                # Пользователи, профили, авторизация
│   ├── jobs/                    # Вакансии
│   ├── applications/            # Отклики + чат
│   ├── tests_system/            # Тесты навыков
│   ├── analytics/               # Анализ вакансий, матчинг, сравнение, избранное
│   ├── config/                  # Настройки Django, URL, seed_data
│   ├── templates/               # HTML-шаблоны веб-интерфейса
│   ├── requirements.txt         # Python-зависимости
│   ├── manage.py
│   └── .env                     # Переменные окружения (не в git!)
├── frontend_app/                # Flutter мобильное приложение
│   ├── lib/
│   │   ├── main.dart            # Точка входа, навигация
│   │   ├── services/            # API-клиент, JWT
│   │   ├── screens/             # Экраны приложения
│   │   └── widgets/             # Общие виджеты
│   └── pubspec.yaml             # Flutter-зависимости
├── docker-compose.yml
├── Dockerfile
└── SETUP.md                     # ← этот файл
```

---

## 6. API-эндпоинты (основные)

### Аутентификация
```
POST /api/accounts/register/          # Регистрация
POST /api/accounts/login/             # Вход (JWT)
POST /api/accounts/token/refresh/     # Обновление токена
```

### Вакансии
```
GET    /api/jobs/                      # Список (фильтры: level, salary_min, salary_max, search)
GET    /api/jobs/{id}/                 # Детали вакансии
POST   /api/jobs/                      # Создать (HR)
```

### Отклики
```
GET    /api/applications/              # Мои отклики / отклики на мои вакансии
POST   /api/applications/              # Откликнуться
PATCH  /api/applications/{id}/status/  # Изменить статус (HR)
GET    /api/applications/stats/        # Статистика HR
```

### Чат
```
GET    /api/applications/{id}/messages/  # Сообщения
POST   /api/applications/{id}/send/      # Отправить сообщение
```

### Аналитика
```
GET    /api/analytics/analyze/{job_id}/  # Анализ вакансии
POST   /api/analytics/match/             # Матчинг навыков
POST   /api/analytics/compare/           # Сравнение вакансий
```

### Тесты
```
GET    /api/tests/                     # Список тестов
GET    /api/tests/{id}/                # Вопросы теста
POST   /api/tests/{id}/submit/         # Сдать тест
```

---

## 7. Возможные проблемы

| Проблема | Решение |
|---|---|
| `psycopg2` не устанавливается | Установите `psycopg2-binary` или PostgreSQL dev-библиотеки |
| Ошибка подключения к БД | Проверьте `.env`, убедитесь что PostgreSQL запущен |
| Flutter: «Ошибка подключения к серверу» | Проверьте `baseUrl` в `api_service.dart` и что Django запущен |
| `No such table` | Запустите `python manage.py migrate` |
| Пустая БД после миграции | Запустите `python manage.py seed_data` |
| CORS-ошибки в браузере | Django уже настроен с `django-cors-headers` |
