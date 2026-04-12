# Job Platform - Дипломный проект | Дорожная карта разработки

## 🎯 Context

**Job Platform** — дипломный проект на Django для поиска работы с фокусом на справедливые требования для Junior разработчиков. Проект находится на **40% готовности**: модели спроектированы, views используют шаблоны, но **нет REST API, тестов и фронтенда**.

**Сроки**: 2-3 недели до сдачи
**MVP Requirements**: REST API + простой фронтенд + базовые тесты (50%+ coverage)
**Аутентификация**: Без защиты для REST API (простой MVP)

---

## ✅ Рекомендуемый подход

Разбиваем на **4 фазы** (каждая 3-5 дней), применяя best practices из claude-code-best-practice:

### **Фаза 1: REST API Preparation (Дни 1-3)**
Превратить существующий код в полноценное REST API с использованием DRF.

**Что сделать:**
1. Создать serializers для всех моделей
2. Преобразовать views → ViewSets + Routers
3. Добавить DRF permission classes (базовые)
4. Инициализировать БД миграции

**Критические файлы для изменения:**
- `backend/accounts/serializers.py` (новый)
- `backend/accounts/views.py` (переписать)
- `backend/jobs/serializers.py` (новый)
- `backend/jobs/views.py` (переписать)
- `backend/applications/serializers.py` (новый)
- `backend/applications/views.py` (переписать)
- `backend/tests_system/serializers.py` (новый)
- `backend/tests_system/views.py` (переписать)
- `backend/config/urls.py` (добавить Routers)

### **Фаза 2: Database & Migrations (Дни 2-3)**
Инициализировать PostgreSQL и создать миграции.

**Что сделать:**
1. Запустить `python manage.py makemigrations`
2. Запустить `python manage.py migrate`
3. Создать тестовые данные (fixtures)
4. Проверить все endpoint'ы в Postman

**Критические файлы:**
- `backend/*/migrations/` (автогенерированные)

### **Фаза 3: Testing Framework (Дни 4-5)**
Написать минимальные тесты (50%+ coverage) для основных endpoint'ов.

**Что сделать:**
1. Создать `tests.py` в каждом приложении
2. Написать TestCase для каждого ViewSet
3. Использовать DRF APITestCase
4. Запустить `coverage run --source='.' manage.py test`

**Критические файлы:**
- `backend/accounts/tests.py` (новый)
- `backend/jobs/tests.py` (новый)
- `backend/applications/tests.py` (новый)
- `backend/tests_system/tests.py` (новый)

### **Фаза 4: Frontend & Documentation (Дни 6-7)**
Простой HTML фронтенд для MVP + документация API.

**Что сделать:**
1. Создать базовые HTML шаблоны для вывода данных
2. Добавить JavaScript для вызовов API
3. Добавить Swagger документацию
4. Протестировать весь workflow

**Критические файлы:**
- `backend/templates/jobs/list.html` (обновить)
- `backend/templates/jobs/detail.html` (обновить)
- `backend/static/js/api.js` (новый)
- `backend/config/settings.py` (добавить drf-spectacular)

---

## 📋 Фаза 1: REST API Preparation (PRIORITY)

### Шаг 1.1: Создать serializers для accounts

**Файл**: `backend/accounts/serializers.py`

```python
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'role', 'avatar', 'bio', 'portfolio_url', 'github_url', 'company_name', 'company_description', 'created_at']
```

### Шаг 1.2: Преобразовать views → ViewSets

**Файл**: `backend/accounts/views.py` (переписать)

```python
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
```

### Шаг 1.3: Обновить URLs с Routers

**Файл**: `backend/config/urls.py`

```python
from rest_framework.routers import DefaultRouter
from accounts.views import UserProfileViewSet

router = DefaultRouter()
router.register('users', UserProfileViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

### Шаг 1.4: Аналогично для jobs, applications, tests_system

Повторить процесс для других приложений.

---

## 🧪 Фаза 3: Testing Framework

### Шаг 3.1: Создать базовые тесты для accounts

**Файл**: `backend/accounts/tests.py`

```python
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.profile = UserProfile.objects.create(user=self.user, role='junior')
    
    def test_get_user_profile(self):
        response = self.client.get(f'/api/users/{self.profile.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'testuser')
```

### Шаг 3.2: Повторить для jobs, applications, tests_system

---

## 📁 Структура коммитов (Git Commit Rules из CLAUDE.md)

**ВАЖНО**: Один коммит = один файл!

```bash
# Коммит 1
git add backend/accounts/serializers.py
git commit -m "Add UserProfile serializers for REST API"

# Коммит 2
git add backend/accounts/views.py
git commit -m "Convert accounts views to DRF ViewSets"

# Коммит 3
git add backend/config/urls.py
git commit -m "Add REST API routers to root urls"

# Коммит 4
git add backend/accounts/tests.py
git commit -m "Add API tests for user profiles"
```

---

## 🚀 Verification & Testing

### Phase 1 Verification (REST API)
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

# Тест endpoint'ов в браузере/Postman
GET http://localhost:8000/api/users/
POST http://localhost:8000/api/users/
GET http://localhost:8000/api/jobs/
```

### Phase 3 Verification (Tests)
```bash
python manage.py test
coverage run --source='.' manage.py test
coverage report -m
# Ожидаемый результат: 50%+ coverage
```

### Phase 4 Verification (Frontend)
```bash
# Открыть браузер на http://localhost:8000
# Проверить список вакансий
# Проверить фильтрацию по junior_friendly
# Проверить создание заявки
```

---

## 🔄 Claude Code Best Practices применены

1. **CLAUDE.md** ✅ — Уже создан с инструкциями для проекта
2. **Plan Mode** ✅ — Используется для планирования архитектуры
3. **Git Commits** ✅ — Один файл = один коммит (как в best-practice репо)
4. **Workflow** ✅ — Research → Plan → Execute → Test → Ship
5. **Serializers** ✅ — DRF serializers вместо forms (как в best practice)

---

## 📊 Progress Tracking

| Phase | Duration | Status | Start | End |
|-------|----------|--------|-------|-----|
| REST API Preparation | 3 дня | TODO | Day 1 | Day 3 |
| Database & Migrations | 1 день | TODO | Day 2 | Day 3 |
| Testing Framework | 2 дня | TODO | Day 4 | Day 5 |
| Frontend & Docs | 2 дня | TODO | Day 6 | Day 7 |
| **TOTAL** | **7 дней** | - | - | - |

---

## 🎯 Success Criteria

✅ Все API endpoint'ы работают через `/api/*` URL
✅ Database миграции созданы и применены
✅ Минимум 50% code coverage
✅ HTML фронтенд показывает данные из API
✅ Swagger документация доступна
✅ Проект готов к деплою на Production

---

**Plan Created**: 2026-04-12 | **Target Deadline**: 2026-04-19 (7 дней)
