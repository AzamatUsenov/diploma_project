"""
Management command to seed the database with realistic mock data.

Usage:
    python manage.py seed_data          # Create all mock data
    python manage.py seed_data --clear  # Clear existing data first
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from jobs.models import Job, JobTag
from tests_system.models import SkillTest, Question
from analytics.job_analyzer import analyze_job


COMPANIES = [
    {'name': 'Kaspi.kz', 'desc': 'Крупнейший финтех Казахстана'},
    {'name': 'Kolesa Group', 'desc': 'Маркетплейс объявлений (Kolesa.kz, Krisha.kz)'},
    {'name': 'DAR', 'desc': 'Технологическая компания (DAR Ecosystem)'},
    {'name': 'Chocofamily', 'desc': 'Экосистема онлайн-сервисов'},
    {'name': 'BTS Digital', 'desc': 'Цифровые решения для государства'},
    {'name': 'One Technologies', 'desc': 'Разработка платежных систем'},
    {'name': 'Beeline KZ', 'desc': 'Телеком оператор'},
    {'name': 'Freedom Finance', 'desc': 'Инвестиционная платформа'},
    {'name': 'Halyk Bank IT', 'desc': 'IT подразделение Halyk Bank'},
    {'name': 'JuSan Bank', 'desc': 'Цифровой банк'},
]

APPLICANTS = [
    {
        'username': 'aidana_junior',
        'email': 'aidana@example.com',
        'first_name': 'Aidana',
        'last_name': 'Nurbekova',
        'role': 'applicant',
        'level': 'junior',
        'skills': ['Python', 'HTML', 'CSS', 'JavaScript', 'Git', 'SQL'],
        'bio': 'Выпускница KBTU, хочу стать backend разработчиком. Изучаю Django.',
    },
    {
        'username': 'arman_mid',
        'email': 'arman@example.com',
        'first_name': 'Arman',
        'last_name': 'Serikbaev',
        'role': 'applicant',
        'level': 'mid',
        'skills': ['Python', 'Django', 'DRF', 'PostgreSQL', 'Docker', 'React', 'TypeScript', 'Git', 'Linux'],
        'bio': '2 года опыта в backend разработке. Работал в стартапе.',
    },
    {
        'username': 'dana_senior',
        'email': 'dana@example.com',
        'first_name': 'Dana',
        'last_name': 'Karimova',
        'role': 'applicant',
        'level': 'senior',
        'skills': ['Python', 'Django', 'FastAPI', 'PostgreSQL', 'Docker', 'Kubernetes', 'AWS', 'Redis', 'Kafka', 'Microservices', 'System Design', 'CI/CD'],
        'bio': '6 лет опыта. Tech Lead в Kolesa Group.',
    },
    {
        'username': 'timur_junior',
        'email': 'timur@example.com',
        'first_name': 'Timur',
        'last_name': 'Orazov',
        'role': 'applicant',
        'level': 'junior',
        'skills': ['JavaScript', 'React', 'HTML', 'CSS', 'Git'],
        'bio': 'Самоучка, прошёл курсы по frontend. Ищу первую работу.',
    },
]

HR_USERS = [
    {
        'username': 'hr_kaspi',
        'email': 'hr@kaspi.kz',
        'first_name': 'Madina',
        'last_name': 'HR',
        'company': 'Kaspi.kz',
    },
    {
        'username': 'hr_kolesa',
        'email': 'hr@kolesa.kz',
        'first_name': 'Aliya',
        'last_name': 'HR',
        'company': 'Kolesa Group',
    },
    {
        'username': 'hr_dar',
        'email': 'hr@dar.io',
        'first_name': 'Nursultan',
        'last_name': 'HR',
        'company': 'DAR',
    },
]

JOBS = [
    # --- Honest junior jobs ---
    {
        'title': 'Junior Python Developer',
        'company': 'Kaspi.kz',
        'location': 'Almaty',
        'description': 'Ищем начинающего Python разработчика в команду платежей. Обучение на месте, менторство от senior разработчиков.',
        'requirements_text': 'Python basics, HTML, CSS, Git. Готовность учиться. Базовое понимание SQL.',
        'level': 'junior',
        'salary_min': 250000,
        'salary_max': 400000,
        'training_provided': True,
        'experience_years': 0,
        'is_remote': False,
        'tech_stack': ['Python', 'HTML', 'CSS', 'Git'],
    },
    {
        'title': 'Junior Frontend Developer',
        'company': 'Kolesa Group',
        'location': 'Almaty',
        'description': 'Команда Krisha.kz ищет начинающего фронтенд разработчика. У нас есть менторская программа.',
        'requirements_text': 'JavaScript, HTML, CSS. Желательно React, но не обязательно. Git basics.',
        'level': 'junior',
        'salary_min': 200000,
        'salary_max': 350000,
        'training_provided': True,
        'experience_years': 0,
        'is_remote': False,
        'tech_stack': ['JavaScript', 'HTML', 'CSS', 'React'],
    },
    {
        'title': 'Стажёр Backend (Django)',
        'company': 'Chocofamily',
        'location': 'Almaty',
        'description': 'Стажировка на 3 месяца с возможностью трудоустройства. Полное обучение.',
        'requirements_text': 'Python или любой другой язык программирования. Желание учиться. Базы данных — плюс.',
        'level': 'junior',
        'salary_min': 150000,
        'salary_max': 250000,
        'training_provided': True,
        'experience_years': 0,
        'is_remote': False,
        'tech_stack': ['Python', 'Django'],
    },
    {
        'title': 'Junior QA Engineer',
        'company': 'BTS Digital',
        'location': 'Astana',
        'description': 'Начинающий тестировщик в команду eGov проектов.',
        'requirements_text': 'Базовое понимание тестирования. SQL основы. Git. Внимательность к деталям.',
        'level': 'junior',
        'salary_min': 200000,
        'salary_max': 300000,
        'training_provided': True,
        'experience_years': 0,
        'is_remote': False,
        'tech_stack': ['SQL', 'Git'],
    },

    # --- Inflated "junior" jobs (overqualified requirements) ---
    {
        'title': 'Junior Python Developer',
        'company': 'Freedom Finance',
        'location': 'Almaty',
        'description': 'Ищем junior разработчика для финтех платформы.',
        'requirements_text': 'Python, Django, Docker, Kubernetes, AWS, PostgreSQL, Redis, CI/CD, Microservices. Опыт от 3 лет. Знание System Design.',
        'level': 'junior',
        'salary_min': 300000,
        'salary_max': 500000,
        'training_provided': False,
        'experience_years': 3,
        'is_remote': False,
        'tech_stack': ['Python', 'Django', 'Docker', 'AWS', 'Kubernetes'],
    },
    {
        'title': 'Junior Full-Stack Developer',
        'company': 'JuSan Bank',
        'location': 'Almaty',
        'description': 'Junior позиция в команду онлайн-банкинга.',
        'requirements_text': 'React, TypeScript, Node.js, Python, Django, PostgreSQL, Docker, Kubernetes, CI/CD, GraphQL, Redis, Elasticsearch. 2+ years experience.',
        'level': 'junior',
        'salary_min': 350000,
        'salary_max': 550000,
        'training_provided': False,
        'experience_years': 2,
        'is_remote': False,
        'tech_stack': ['React', 'TypeScript', 'Python', 'Django', 'Docker'],
    },
    {
        'title': 'Junior DevOps Engineer',
        'company': 'One Technologies',
        'location': 'Astana',
        'description': 'Junior DevOps в команду инфраструктуры.',
        'requirements_text': 'Linux, Docker, Kubernetes, Terraform, AWS, CI/CD, Ansible, Python scripting, Prometheus, Grafana. Минимум 2 года опыта.',
        'level': 'junior',
        'salary_min': 400000,
        'salary_max': 600000,
        'training_provided': False,
        'experience_years': 2,
        'is_remote': True,
        'tech_stack': ['Docker', 'Kubernetes', 'Terraform', 'AWS'],
    },

    # --- Honest mid jobs ---
    {
        'title': 'Middle Python Developer',
        'company': 'Kaspi.kz',
        'location': 'Almaty',
        'description': 'Backend разработчик в команду маркетплейса. Работа с высоконагруженными системами.',
        'requirements_text': 'Python, Django или FastAPI, PostgreSQL, Docker, Redis. Опыт 2-3 года. Понимание REST API.',
        'level': 'mid',
        'salary_min': 600000,
        'salary_max': 900000,
        'training_provided': False,
        'experience_years': 2,
        'is_remote': False,
        'tech_stack': ['Python', 'Django', 'PostgreSQL', 'Docker', 'Redis'],
    },
    {
        'title': 'Middle Frontend Developer (React)',
        'company': 'Kolesa Group',
        'location': 'Almaty',
        'description': 'React разработчик для Kolesa.kz. Команда из 8 человек.',
        'requirements_text': 'React, TypeScript, HTML, CSS, Git. Опыт с REST API. 2+ года коммерческого опыта.',
        'level': 'mid',
        'salary_min': 550000,
        'salary_max': 850000,
        'training_provided': False,
        'experience_years': 2,
        'is_remote': True,
        'tech_stack': ['React', 'TypeScript', 'HTML', 'CSS'],
    },
    {
        'title': 'Middle Java Developer',
        'company': 'Halyk Bank IT',
        'location': 'Almaty',
        'description': 'Java разработчик для банковских систем.',
        'requirements_text': 'Java, Spring Boot, PostgreSQL, Docker, CI/CD. Опыт работы в команде 2-3 года.',
        'level': 'mid',
        'salary_min': 700000,
        'salary_max': 1000000,
        'training_provided': False,
        'experience_years': 2,
        'is_remote': False,
        'tech_stack': ['Java', 'Spring Boot', 'PostgreSQL', 'Docker'],
    },
    {
        'title': 'Middle Go Developer',
        'company': 'DAR',
        'location': 'Almaty',
        'description': 'Go разработчик для микросервисной платформы DAR Ecosystem.',
        'requirements_text': 'Go, gRPC, Docker, PostgreSQL, Redis. Опыт 2+ года. Понимание микросервисной архитектуры.',
        'level': 'mid',
        'salary_min': 650000,
        'salary_max': 950000,
        'training_provided': False,
        'experience_years': 2,
        'is_remote': True,
        'tech_stack': ['Go', 'Docker', 'PostgreSQL', 'Redis'],
    },
    {
        'title': 'Middle Mobile Developer (Flutter)',
        'company': 'Chocofamily',
        'location': 'Almaty',
        'description': 'Flutter разработчик для мобильных приложений экосистемы.',
        'requirements_text': 'Flutter, Dart, REST API, Git. Опыт публикации в App Store / Google Play.',
        'level': 'mid',
        'salary_min': 500000,
        'salary_max': 800000,
        'training_provided': False,
        'experience_years': 2,
        'is_remote': False,
        'tech_stack': ['Flutter', 'REST API', 'Git'],
    },

    # --- Slightly inflated mid jobs ---
    {
        'title': 'Middle Backend Developer',
        'company': 'Beeline KZ',
        'location': 'Almaty',
        'description': 'Backend для телеком систем.',
        'requirements_text': 'Python, Django, PostgreSQL, Docker, Kubernetes, AWS, Kafka, Elasticsearch, Redis, Microservices, System Design, CI/CD, Terraform. 3-5 лет.',
        'level': 'mid',
        'salary_min': 700000,
        'salary_max': 1100000,
        'training_provided': False,
        'experience_years': 4,
        'is_remote': False,
        'tech_stack': ['Python', 'Django', 'Kubernetes', 'AWS', 'Kafka'],
    },

    # --- Senior jobs ---
    {
        'title': 'Senior Python Developer',
        'company': 'Kaspi.kz',
        'location': 'Almaty',
        'description': 'Tech Lead позиция в команду Super App. Проектирование архитектуры, менторство.',
        'requirements_text': 'Python, Django/FastAPI, PostgreSQL, Docker, Kubernetes, AWS, Redis, Kafka, Microservices, System Design, CI/CD. 5+ лет опыта. Опыт менторства.',
        'level': 'senior',
        'salary_min': 1200000,
        'salary_max': 2000000,
        'training_provided': False,
        'experience_years': 5,
        'is_remote': False,
        'tech_stack': ['Python', 'FastAPI', 'Kubernetes', 'AWS', 'Kafka'],
    },
    {
        'title': 'Senior Frontend Architect',
        'company': 'Kolesa Group',
        'location': 'Almaty',
        'description': 'Архитектор фронтенда для всех продуктов группы.',
        'requirements_text': 'React, TypeScript, Next.js, Node.js, Webpack, CI/CD, System Design. 5+ years. Experience leading a team.',
        'level': 'senior',
        'salary_min': 1000000,
        'salary_max': 1800000,
        'training_provided': False,
        'experience_years': 5,
        'is_remote': True,
        'tech_stack': ['React', 'TypeScript', 'Next.js', 'Node.js'],
    },
    {
        'title': 'Senior DevOps / SRE',
        'company': 'DAR',
        'location': 'Almaty',
        'description': 'SRE инженер для обеспечения надёжности DAR Ecosystem.',
        'requirements_text': 'Kubernetes, AWS/GCP, Terraform, Docker, CI/CD, Linux, Python/Go scripting, Prometheus, Grafana. 5+ лет.',
        'level': 'senior',
        'salary_min': 1300000,
        'salary_max': 2200000,
        'training_provided': False,
        'experience_years': 5,
        'is_remote': True,
        'tech_stack': ['Kubernetes', 'AWS', 'Terraform', 'Docker', 'Linux'],
    },
    {
        'title': 'Engineering Manager',
        'company': 'Freedom Finance',
        'location': 'Almaty',
        'description': 'Руководитель команды из 10 разработчиков.',
        'requirements_text': 'Глубокое знание Python или Java, Microservices, System Design, AWS, Kubernetes. 7+ лет разработки, 2+ года управления.',
        'level': 'senior',
        'salary_min': 1500000,
        'salary_max': 2500000,
        'training_provided': False,
        'experience_years': 7,
        'is_remote': False,
        'tech_stack': ['Python', 'Microservices', 'AWS', 'Kubernetes'],
    },

    # --- Remote-friendly jobs ---
    {
        'title': 'Junior React Developer (Remote)',
        'company': 'DAR',
        'location': 'Kazakhstan (Remote)',
        'description': 'Полностью удалённая позиция для начинающего React разработчика.',
        'requirements_text': 'React, JavaScript, HTML, CSS, Git. Будем учить TypeScript на месте.',
        'level': 'junior',
        'salary_min': 250000,
        'salary_max': 400000,
        'training_provided': True,
        'experience_years': 0,
        'is_remote': True,
        'tech_stack': ['React', 'JavaScript', 'HTML', 'CSS'],
    },
    {
        'title': 'Middle Data Engineer (Remote)',
        'company': 'Kaspi.kz',
        'location': 'Kazakhstan (Remote)',
        'description': 'Data инженер для построения аналитических пайплайнов.',
        'requirements_text': 'Python, SQL, Spark, Kafka, Airflow, PostgreSQL. 2-3 года опыта с данными.',
        'level': 'mid',
        'salary_min': 800000,
        'salary_max': 1200000,
        'training_provided': False,
        'experience_years': 2,
        'is_remote': True,
        'tech_stack': ['Python', 'SQL', 'Spark', 'Kafka'],
    },

    # --- More variety ---
    {
        'title': 'Junior iOS Developer',
        'company': 'Chocofamily',
        'location': 'Almaty',
        'description': 'Начинающий iOS разработчик. Менторство от senior.',
        'requirements_text': 'Swift basics, понимание iOS lifecycle. Git.',
        'level': 'junior',
        'salary_min': 250000,
        'salary_max': 380000,
        'training_provided': True,
        'experience_years': 0,
        'is_remote': False,
        'tech_stack': ['Swift', 'iOS', 'Git'],
    },
    {
        'title': 'Middle C# Developer (.NET)',
        'company': 'Halyk Bank IT',
        'location': 'Almaty',
        'description': '.NET разработчик для внутренних банковских систем.',
        'requirements_text': 'C#, .NET, SQL Server, REST API. Опыт 2-3 года.',
        'level': 'mid',
        'salary_min': 600000,
        'salary_max': 950000,
        'training_provided': False,
        'experience_years': 2,
        'is_remote': False,
        'tech_stack': ['C#', '.NET', 'SQL'],
    },
    {
        'title': 'Junior Data Analyst',
        'company': 'BTS Digital',
        'location': 'Astana',
        'description': 'Аналитик данных для eGov проектов. Обучение на месте.',
        'requirements_text': 'SQL, Python basics, Excel. Аналитическое мышление.',
        'level': 'junior',
        'salary_min': 200000,
        'salary_max': 350000,
        'training_provided': True,
        'experience_years': 0,
        'is_remote': False,
        'tech_stack': ['SQL', 'Python'],
    },
    {
        'title': 'Middle PHP Developer (Laravel)',
        'company': 'One Technologies',
        'location': 'Astana',
        'description': 'PHP разработчик для платежных систем.',
        'requirements_text': 'PHP, Laravel, MySQL, Docker, REST API. 2+ года опыта.',
        'level': 'mid',
        'salary_min': 500000,
        'salary_max': 750000,
        'training_provided': False,
        'experience_years': 2,
        'is_remote': False,
        'tech_stack': ['PHP', 'Laravel', 'MySQL', 'Docker'],
    },
    {
        'title': 'Senior ML Engineer',
        'company': 'Kaspi.kz',
        'location': 'Almaty',
        'description': 'ML инженер для рекомендательной системы маркетплейса.',
        'requirements_text': 'Python, TensorFlow/PyTorch, Machine Learning, Deep Learning, Spark, Docker, AWS. 4+ года в ML.',
        'level': 'senior',
        'salary_min': 1500000,
        'salary_max': 2500000,
        'training_provided': False,
        'experience_years': 4,
        'is_remote': False,
        'tech_stack': ['Python', 'TensorFlow', 'PyTorch', 'AWS', 'Spark'],
    },
    {
        'title': 'Junior Python Developer',
        'company': 'Beeline KZ',
        'location': 'Almaty',
        'description': 'Джуниор Python для автоматизации телеком-процессов.',
        'requirements_text': 'Python, SQL, Linux basics, Git. Обучаем Django.',
        'level': 'junior',
        'salary_min': 220000,
        'salary_max': 350000,
        'training_provided': True,
        'experience_years': 0,
        'is_remote': False,
        'tech_stack': ['Python', 'SQL', 'Linux'],
    },
    {
        'title': 'Middle Node.js Developer',
        'company': 'JuSan Bank',
        'location': 'Almaty',
        'description': 'Node.js разработчик для API цифрового банка.',
        'requirements_text': 'Node.js, TypeScript, Express, PostgreSQL, Docker, Redis. 2+ года.',
        'level': 'mid',
        'salary_min': 600000,
        'salary_max': 900000,
        'training_provided': False,
        'experience_years': 2,
        'is_remote': True,
        'tech_stack': ['Node.js', 'TypeScript', 'Express', 'PostgreSQL'],
    },
    {
        'title': 'Junior Backend Developer',
        'company': 'DAR',
        'location': 'Almaty',
        'description': 'Начинающий backend разработчик для Go микросервисов.',
        'requirements_text': 'Go или Python, SQL, Git. Готовность изучать Go если не знаете.',
        'level': 'junior',
        'salary_min': 280000,
        'salary_max': 420000,
        'training_provided': True,
        'experience_years': 0,
        'is_remote': False,
        'tech_stack': ['Go', 'Python', 'SQL'],
    },
    {
        'title': 'Senior Java Architect',
        'company': 'Halyk Bank IT',
        'location': 'Almaty',
        'description': 'Архитектор для core banking систем.',
        'requirements_text': 'Java, Spring Boot, Hibernate, Kubernetes, Oracle, Microservices, System Design. 6+ лет.',
        'level': 'senior',
        'salary_min': 1400000,
        'salary_max': 2300000,
        'training_provided': False,
        'experience_years': 6,
        'is_remote': False,
        'tech_stack': ['Java', 'Spring Boot', 'Kubernetes', 'Oracle'],
    },
    {
        'title': 'Middle Android Developer',
        'company': 'Kolesa Group',
        'location': 'Almaty',
        'description': 'Android разработчик для Kolesa.kz мобильного приложения.',
        'requirements_text': 'Kotlin, Android SDK, REST API, Git. 2+ года опыта.',
        'level': 'mid',
        'salary_min': 550000,
        'salary_max': 850000,
        'training_provided': False,
        'experience_years': 2,
        'is_remote': False,
        'tech_stack': ['Kotlin', 'Android', 'REST API'],
    },
]

TAGS = [
    'Python', 'JavaScript', 'Java', 'Go', 'React', 'Django',
    'Remote', 'Fintech', 'E-commerce', 'Backend', 'Frontend',
    'Mobile', 'DevOps', 'Data', 'Junior-Friendly',
]

TESTS_DATA = [
    {
        'title': 'Python Fundamentals',
        'language': 'python',
        'description': 'Проверьте ваши знания основ Python: типы данных, функции, ООП.',
        'difficulty': 'easy',
        'questions': [
            {'text': 'Какой тип данных вернёт выражение type(42)?', 'a': 'int', 'b': 'float', 'c': 'str', 'd': 'number', 'correct': 'a'},
            {'text': 'Что делает метод list.append()?', 'a': 'Удаляет элемент', 'b': 'Добавляет элемент в конец', 'c': 'Сортирует список', 'd': 'Возвращает длину', 'correct': 'b'},
            {'text': 'Как создать виртуальное окружение?', 'a': 'pip install venv', 'b': 'python -m venv env', 'c': 'virtualenv --create', 'd': 'python new venv', 'correct': 'b'},
            {'text': 'Что такое list comprehension?', 'a': 'Тип данных', 'b': 'Паттерн проектирования', 'c': 'Сокращённый синтаксис создания списка', 'd': 'Метод списка', 'correct': 'c'},
            {'text': 'Какой результат: len("Hello")?', 'a': '4', 'b': '5', 'c': '6', 'd': 'Error', 'correct': 'b'},
            {'text': 'Что делает декоратор @staticmethod?', 'a': 'Делает метод приватным', 'b': 'Метод не получает self/cls', 'c': 'Метод выполняется один раз', 'd': 'Метод становится асинхронным', 'correct': 'b'},
            {'text': 'Как обработать исключение в Python?', 'a': 'catch/throw', 'b': 'try/except', 'c': 'handle/error', 'd': 'begin/rescue', 'correct': 'b'},
            {'text': 'Что вернёт [1,2,3][1:2]?', 'a': '[1, 2]', 'b': '[2]', 'c': '[2, 3]', 'd': '[1]', 'correct': 'b'},
        ],
    },
    {
        'title': 'JavaScript Essentials',
        'language': 'javascript',
        'description': 'Основы JavaScript: переменные, функции, DOM, ES6+.',
        'difficulty': 'easy',
        'questions': [
            {'text': 'Чем отличается let от var?', 'a': 'Ничем', 'b': 'let имеет блочную область видимости', 'c': 'let быстрее', 'd': 'var устарел полностью', 'correct': 'b'},
            {'text': 'Что вернёт typeof null?', 'a': 'null', 'b': 'undefined', 'c': 'object', 'd': 'boolean', 'correct': 'c'},
            {'text': 'Что такое Promise?', 'a': 'Тип данных', 'b': 'Объект для асинхронных операций', 'c': 'Метод массива', 'd': 'DOM элемент', 'correct': 'b'},
            {'text': 'Как объявить стрелочную функцию?', 'a': 'function => {}', 'b': '() => {}', 'c': 'arrow() {}', 'd': 'fn => {}', 'correct': 'b'},
            {'text': 'Что делает Array.map()?', 'a': 'Фильтрует массив', 'b': 'Находит элемент', 'c': 'Создаёт новый массив с результатом функции', 'd': 'Сортирует массив', 'correct': 'c'},
            {'text': 'Что такое "use strict"?', 'a': 'Библиотека', 'b': 'Режим строгого синтаксиса', 'c': 'Тип данных', 'd': 'Комментарий', 'correct': 'b'},
        ],
    },
    {
        'title': 'Django & DRF',
        'language': 'python',
        'description': 'Тест на знание Django и Django REST Framework.',
        'difficulty': 'medium',
        'questions': [
            {'text': 'Что такое ORM в Django?', 'a': 'Шаблонизатор', 'b': 'Объектно-реляционное отображение', 'c': 'Роутер URL', 'd': 'Менеджер пакетов', 'correct': 'b'},
            {'text': 'Какой файл содержит настройки Django проекта?', 'a': 'urls.py', 'b': 'models.py', 'c': 'settings.py', 'd': 'views.py', 'correct': 'c'},
            {'text': 'Что делает makemigrations?', 'a': 'Применяет миграции к БД', 'b': 'Создаёт файлы миграций', 'c': 'Удаляет миграции', 'd': 'Откатывает миграции', 'correct': 'b'},
            {'text': 'Для чего нужен Serializer в DRF?', 'a': 'Для роутинга', 'b': 'Для авторизации', 'c': 'Для валидации и преобразования данных', 'd': 'Для кэширования', 'correct': 'c'},
            {'text': 'Что такое ViewSet в DRF?', 'a': 'HTML шаблон', 'b': 'Класс с набором CRUD действий', 'c': 'Middleware', 'd': 'Фильтр', 'correct': 'b'},
            {'text': 'Как создать суперпользователя?', 'a': 'manage.py createadmin', 'b': 'manage.py createsuperuser', 'c': 'manage.py adduser --admin', 'd': 'manage.py superuser', 'correct': 'b'},
            {'text': 'Что делает select_related()?', 'a': 'Фильтрует queryset', 'b': 'Выполняет JOIN для уменьшения запросов', 'c': 'Выбирает конкретные поля', 'd': 'Удаляет связанные объекты', 'correct': 'b'},
        ],
    },
    {
        'title': 'React Basics',
        'language': 'react',
        'description': 'Основы React: компоненты, хуки, state management.',
        'difficulty': 'medium',
        'questions': [
            {'text': 'Что такое JSX?', 'a': 'Библиотека', 'b': 'Расширение синтаксиса JavaScript', 'c': 'Фреймворк', 'd': 'База данных', 'correct': 'b'},
            {'text': 'Для чего нужен useState?', 'a': 'Для роутинга', 'b': 'Для HTTP запросов', 'c': 'Для управления состоянием компонента', 'd': 'Для стилей', 'correct': 'c'},
            {'text': 'Что такое Virtual DOM?', 'a': 'Реальный DOM', 'b': 'Лёгкая копия DOM для оптимизации', 'c': 'База данных', 'd': 'CSS фреймворк', 'correct': 'b'},
            {'text': 'Как передать данные от родителя к дочернему компоненту?', 'a': 'Через state', 'b': 'Через props', 'c': 'Через context только', 'd': 'Через localStorage', 'correct': 'b'},
            {'text': 'Что делает useEffect?', 'a': 'Создаёт компонент', 'b': 'Выполняет побочные эффекты', 'c': 'Стилизует компонент', 'd': 'Удаляет компонент', 'correct': 'b'},
        ],
    },
    {
        'title': 'SQL & Databases',
        'language': 'general',
        'description': 'Знание SQL: запросы, JOIN, индексы, нормализация.',
        'difficulty': 'easy',
        'questions': [
            {'text': 'Что делает оператор SELECT?', 'a': 'Удаляет данные', 'b': 'Выбирает данные из таблицы', 'c': 'Создаёт таблицу', 'd': 'Обновляет данные', 'correct': 'b'},
            {'text': 'Что такое PRIMARY KEY?', 'a': 'Индекс', 'b': 'Уникальный идентификатор строки', 'c': 'Внешний ключ', 'd': 'Тип данных', 'correct': 'b'},
            {'text': 'Чем INNER JOIN отличается от LEFT JOIN?', 'a': 'Ничем', 'b': 'LEFT JOIN включает все строки левой таблицы', 'c': 'INNER JOIN быстрее', 'd': 'LEFT JOIN работает только с 2 таблицами', 'correct': 'b'},
            {'text': 'Что такое индекс в БД?', 'a': 'Тип таблицы', 'b': 'Структура для ускорения поиска', 'c': 'Резервная копия', 'd': 'Тип данных', 'correct': 'b'},
            {'text': 'Что делает GROUP BY?', 'a': 'Сортирует данные', 'b': 'Группирует строки для агрегатных функций', 'c': 'Объединяет таблицы', 'd': 'Фильтрует данные', 'correct': 'b'},
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed database with realistic mock data for the Job Platform'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data first')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            from analytics.models import Favorite
            from applications.models import Application
            from tests_system.models import Answer, TestResult
            Answer.objects.all().delete()
            TestResult.objects.all().delete()
            Favorite.objects.all().delete()
            Application.objects.all().delete()
            Question.objects.all().delete()
            SkillTest.objects.all().delete()
            Job.objects.all().delete()
            JobTag.objects.all().delete()
            UserProfile.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        # 1. Create tags
        self.stdout.write('Creating tags...')
        tags = {}
        for tag_name in TAGS:
            tag, _ = JobTag.objects.get_or_create(name=tag_name)
            tags[tag_name] = tag

        # 2. Create HR users
        self.stdout.write('Creating HR users...')
        hr_users = {}
        for hr_data in HR_USERS:
            user, created = User.objects.get_or_create(
                username=hr_data['username'],
                defaults={
                    'email': hr_data['email'],
                    'first_name': hr_data['first_name'],
                    'last_name': hr_data['last_name'],
                },
            )
            if created:
                user.set_password('test123')
                user.save()
                UserProfile.objects.create(
                    user=user, role='hr',
                    company_name=hr_data['company'],
                    company_description=next(
                        (c['desc'] for c in COMPANIES if c['name'] == hr_data['company']),
                        '',
                    ),
                )
            hr_users[hr_data['company']] = user

        # 3. Create applicants
        self.stdout.write('Creating applicants...')
        for app_data in APPLICANTS:
            user, created = User.objects.get_or_create(
                username=app_data['username'],
                defaults={
                    'email': app_data['email'],
                    'first_name': app_data['first_name'],
                    'last_name': app_data['last_name'],
                },
            )
            if created:
                user.set_password('test123')
                user.save()
                UserProfile.objects.create(
                    user=user,
                    role=app_data['role'],
                    level=app_data['level'],
                    skills=app_data['skills'],
                    bio=app_data['bio'],
                )

        # 4. Create jobs
        self.stdout.write('Creating jobs...')
        for job_data in JOBS:
            company = job_data['company']
            hr_user = hr_users.get(company)
            if not hr_user:
                # Use first HR user as fallback
                hr_user = list(hr_users.values())[0]

            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                company=company,
                defaults={
                    'description': job_data['description'],
                    'location': job_data['location'],
                    'requirements_text': job_data['requirements_text'],
                    'level': job_data['level'],
                    'salary_min': job_data['salary_min'],
                    'salary_max': job_data['salary_max'],
                    'training_provided': job_data['training_provided'],
                    'experience_years': job_data['experience_years'],
                    'is_remote': job_data['is_remote'],
                    'tech_stack': job_data['tech_stack'],
                    'posted_by': hr_user,
                },
            )

            if created:
                # Run analyzer
                analysis = analyze_job(job)
                job.parsed_skills = analysis['parsed_skills']
                job.detected_level = analysis['detected_level']
                job.is_overqualified = analysis['is_overqualified']
                job.honesty_score = analysis['honesty_score']
                job.save()

                # Add tags
                for tech in job_data['tech_stack']:
                    if tech in tags:
                        tags[tech].jobs.add(job)
                if job_data['level'] == 'junior' and job_data['training_provided']:
                    if 'Junior-Friendly' in tags:
                        tags['Junior-Friendly'].jobs.add(job)
                if job_data['is_remote']:
                    if 'Remote' in tags:
                        tags['Remote'].jobs.add(job)

        # 5. Create skill tests
        self.stdout.write('Creating skill tests...')
        for test_data in TESTS_DATA:
            test, created = SkillTest.objects.get_or_create(
                title=test_data['title'],
                defaults={
                    'language': test_data['language'],
                    'description': test_data['description'],
                    'difficulty': test_data['difficulty'],
                },
            )
            if created:
                for i, q_data in enumerate(test_data['questions']):
                    Question.objects.create(
                        test=test,
                        question_type='quiz',
                        text=q_data['text'],
                        order=i + 1,
                        option_a=q_data['a'],
                        option_b=q_data['b'],
                        option_c=q_data['c'],
                        option_d=q_data['d'],
                        correct_answer=q_data['correct'],
                    )

        # Summary
        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created:\n'
            f'  - {User.objects.filter(profile__role="applicant").count()} applicants\n'
            f'  - {User.objects.filter(profile__role="hr").count()} HR users\n'
            f'  - {Job.objects.count()} jobs\n'
            f'  - {JobTag.objects.count()} tags\n'
            f'  - {SkillTest.objects.count()} skill tests\n'
            f'  - {Question.objects.count()} questions\n'
        ))
