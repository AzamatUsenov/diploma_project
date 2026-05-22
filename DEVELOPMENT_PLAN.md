# JobPlatform — Статус разработки

## Текущее состояние: ~90% готовности

Проект полностью функционален. Backend REST API + Flutter мобильное приложение работают.

---

## Реализованные модули

| Модуль | Backend | Frontend | Тесты | Статус |
|--------|---------|----------|-------|--------|
| Аутентификация (JWT) | Done | Done | Done | Complete |
| Профили пользователей | Done | Done | Done | Complete |
| Вакансии (CRUD, фильтры, избранное) | Done | Done | Done | Complete |
| Отклики (workflow статусов) | Done | Done | Done | Complete |
| Чат (сообщения в откликах) | Done | Done | Done | Complete |
| Тесты навыков | Done | Done | Done | Complete |
| Аналитика (анализ, матчинг, сравнение) | Done | Done | Done | Complete |
| Отзывы о компаниях | Done | Done | Done | Complete |
| Уведомления | Done | Done | - | Complete |
| Веб-интерфейс (Django templates) | Done | N/A | - | Complete |
| Загрузка резюме | Done | Done | - | Complete |
| Тёмная тема | N/A | Done | - | Complete |
| Локализация (русский) | N/A | Done | - | Complete |
| Онбординг | N/A | Done | - | Complete |
| PDF-отчёты | Done | - | - | Complete |
| Seed data (демо) | Done | N/A | - | Complete |
| Swagger/ReDoc документация | Done | N/A | - | Complete |

---

## Технологический стек

| Компонент | Технология | Версия |
|-----------|------------|--------|
| Backend | Django + DRF | 4.2 / 3.14 |
| Auth | SimpleJWT | 5.3.1 |
| Database | PostgreSQL / SQLite | 14+ |
| API Docs | drf-spectacular | 0.29.0 |
| Frontend | Flutter (Dart) | 3.9+ |
| PDF | xhtml2pdf | 0.2.17 |
| Deploy | Docker + Gunicorn | - |

---

## Что может потребовать доработки

- Расширение тестового покрытия (notifications, reviews)
- Push-уведомления (Firebase) для мобильного приложения
- Деплой на production (VPS/Cloud)
- Полировка UI/UX на отдельных экранах

---

**Last Updated**: 2026-05-22
