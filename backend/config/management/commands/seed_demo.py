from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import UserProfile
from jobs.models import Job, JobTag
from applications.models import Application, Message
from tests_system.models import SkillTest, Question, TestResult
from notifications.models import Notification
from analytics.models import Favorite


class Command(BaseCommand):
    help = 'Seed database with demo data for development and presentations'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true', help='Delete all existing data before seeding')

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write('Flushing existing data...')
            for model in [Notification, Favorite, Message, TestResult, Application, Question, SkillTest, Job, JobTag, UserProfile]:
                model.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        users = self._create_users()
        jobs = self._create_jobs(users)
        self._create_tags(jobs)
        tests = self._create_tests()
        apps = self._create_applications(users, jobs)
        self._create_messages(apps, users)
        self._create_test_results(users, tests)
        self._create_favorites(users, jobs)

        self.stdout.write(self.style.SUCCESS('\nDemo data seeded successfully!'))
        self.stdout.write(f'  Accounts: {User.objects.filter(is_superuser=False).count()} users')
        self.stdout.write(f'  Jobs: {Job.objects.count()} vacancies')
        self.stdout.write(f'  Applications: {Application.objects.count()}')
        self.stdout.write(f'  Tests: {SkillTest.objects.count()} tests, {Question.objects.count()} questions')
        self.stdout.write(f'  Notifications: {Notification.objects.count()}')
        self.stdout.write('')
        self.stdout.write('  Login credentials (password for all: test1234):')
        for u in User.objects.filter(is_superuser=False).order_by('username'):
            role = getattr(u, 'profile', None)
            self.stdout.write(f'    {u.username} — {role.role if role else "no profile"}')

    def _create_users(self):
        users = {}
        data = [
            ('hr_ivan', 'Ivan', 'Petrov', 'hr@techcorp.kz', 'hr', {'company_name': 'TechCorp', 'company_description': 'Ведущая IT-компания Казахстана'}),
            ('hr_asel', 'Asel', 'Nurbekova', 'asel@webstudio.kz', 'hr', {'company_name': 'WebStudio', 'company_description': 'Веб-студия полного цикла'}),
            ('hr_damir', 'Damir', 'Kairatov', 'damir@cloudsys.kz', 'hr', {'company_name': 'CloudSys', 'company_description': 'Облачные решения для бизнеса'}),
            ('azamat', 'Azamat', 'Usenov', 'azamat@mail.kz', 'applicant', {'level': 'junior', 'skills': ['Python', 'Django', 'HTML', 'CSS', 'Git', 'SQL'], 'bio': 'Выпускник АУЭС, ищу первую работу в IT', 'github_url': 'https://github.com/azamat'}),
            ('dana', 'Dana', 'Serikova', 'dana@mail.kz', 'applicant', {'level': 'junior', 'skills': ['JavaScript', 'React', 'HTML', 'CSS', 'Git'], 'bio': 'Frontend разработчик-новичок'}),
            ('timur', 'Timur', 'Akhmetov', 'timur@mail.kz', 'applicant', {'level': 'mid', 'skills': ['Python', 'Django', 'Docker', 'PostgreSQL', 'React', 'Redis'], 'bio': '2 года опыта в веб-разработке', 'portfolio_url': 'https://timur.dev'}),
            ('aliya', 'Aliya', 'Tulegenova', 'aliya@mail.kz', 'applicant', {'level': 'mid', 'skills': ['Java', 'Spring', 'Docker', 'MySQL', 'Git'], 'bio': 'Java backend разработчик'}),
            ('marat', 'Marat', 'Suleimenov', 'marat@mail.kz', 'applicant', {'level': 'senior', 'skills': ['Python', 'Go', 'Kubernetes', 'AWS', 'Microservices', 'Docker', 'PostgreSQL', 'Redis', 'Kafka'], 'bio': 'Senior backend с 6-летним стажем'}),
            ('nursultan', 'Nursultan', 'Orazov', 'nursultan@mail.kz', 'applicant', {'level': 'junior', 'skills': ['Python', 'HTML', 'CSS', 'Git'], 'bio': 'Только начал изучать программирование'}),
            ('aigul', 'Aigul', 'Bekturova', 'aigul@mail.kz', 'applicant', {'level': 'junior', 'skills': ['JavaScript', 'Node.js', 'HTML', 'CSS', 'MongoDB'], 'bio': 'Fullstack новичок, учусь каждый день'}),
        ]
        for username, first, last, email, role, extra in data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'first_name': first, 'last_name': last},
            )
            if created:
                user.set_password('test1234')
                user.save()
                profile_kwargs = {'user': user, 'role': role}
                for k in ('level', 'skills', 'bio', 'portfolio_url', 'github_url', 'company_name', 'company_description'):
                    if k in extra:
                        profile_kwargs[k] = extra[k]
                UserProfile.objects.create(**profile_kwargs)
                self.stdout.write(f'  + User: {username} ({role})')
            users[username] = user
        return users

    def _create_jobs(self, users):
        jobs = {}
        data = [
            {
                'title': 'Junior Python Developer',
                'company': 'TechCorp', 'location': 'Алматы', 'level': 'junior',
                'salary_min': 250000, 'salary_max': 450000,
                'experience_years': 0, 'is_remote': False, 'training_provided': True,
                'description': 'Ищем junior Python разработчика. Менторство и обучение предоставляется. Работа в офисе в Алматы.',
                'requirements_text': 'Базовое знание Python, основы SQL, Git. Желание учиться.',
                'tech_stack': ['Python', 'Django', 'PostgreSQL', 'Git'],
                'posted_by': users['hr_ivan'], 'honesty_score': 95,
            },
            {
                'title': 'Junior Frontend Developer',
                'company': 'WebStudio', 'location': 'Нур-Султан', 'level': 'junior',
                'salary_min': 200000, 'salary_max': 400000,
                'experience_years': 0, 'is_remote': True, 'training_provided': True,
                'description': 'Удалённая позиция для начинающего фронтенд разработчика. Полное обучение с ментором.',
                'requirements_text': 'HTML, CSS, основы JavaScript. Желание развиваться.',
                'tech_stack': ['HTML', 'CSS', 'JavaScript'],
                'posted_by': users['hr_asel'], 'honesty_score': 98,
            },
            {
                'title': 'Junior JavaScript Developer',
                'company': 'TechCorp', 'location': 'Алматы', 'level': 'junior',
                'salary_min': 300000, 'salary_max': 500000,
                'experience_years': 0, 'is_remote': True, 'training_provided': True,
                'description': 'Начинаем с нуля! Полное обучение и менторство для новичков.',
                'requirements_text': 'Готовность учиться, базовое программирование, логическое мышление.',
                'tech_stack': ['JavaScript', 'Node.js', 'Express'],
                'posted_by': users['hr_ivan'], 'honesty_score': 92,
            },
            {
                'title': 'Junior Python Developer (Inflated)',
                'company': 'FakeCorp', 'location': 'Алматы', 'level': 'junior',
                'salary_min': 180000, 'salary_max': 300000,
                'experience_years': 5, 'is_remote': False, 'training_provided': False,
                'description': 'Ищем "джуниора" с опытом 5+ лет и знанием Kubernetes.',
                'requirements_text': 'Python, Django, Docker, Kubernetes, AWS, React, Microservices, CI/CD. 5+ лет опыта обязательно.',
                'tech_stack': ['Python', 'Django', 'Docker', 'AWS', 'Kubernetes'],
                'posted_by': users['hr_ivan'], 'honesty_score': 12,
                'detected_level': 'senior', 'is_overqualified': True,
            },
            {
                'title': 'Mid React Developer',
                'company': 'WebStudio', 'location': 'Нур-Султан', 'level': 'mid',
                'salary_min': 600000, 'salary_max': 1000000,
                'experience_years': 2, 'is_remote': True, 'training_provided': False,
                'description': 'Требуется опытный React разработчик для фронтенда. Удалённая работа.',
                'requirements_text': '2+ лет опыта с React, знание TypeScript, REST API.',
                'tech_stack': ['React', 'TypeScript', 'Redux', 'Jest'],
                'posted_by': users['hr_asel'], 'honesty_score': 85,
            },
            {
                'title': 'Mid Django Developer',
                'company': 'TechCorp', 'location': 'Алматы', 'level': 'mid',
                'salary_min': 700000, 'salary_max': 1200000,
                'experience_years': 2, 'is_remote': False, 'training_provided': False,
                'description': 'Backend разработчик для расширения нашей платформы.',
                'requirements_text': 'Python, Django, PostgreSQL, Docker. REST API, тестирование.',
                'tech_stack': ['Python', 'Django', 'PostgreSQL', 'Docker'],
                'posted_by': users['hr_ivan'], 'honesty_score': 88,
            },
            {
                'title': 'Mid Java Developer',
                'company': 'CloudSys', 'location': 'Астана', 'level': 'mid',
                'salary_min': 800000, 'salary_max': 1300000,
                'experience_years': 3, 'is_remote': False, 'training_provided': False,
                'description': 'Java разработчик для enterprise проектов.',
                'requirements_text': 'Java, Spring Boot, MySQL, REST API. 3 года опыта.',
                'tech_stack': ['Java', 'Spring', 'MySQL', 'Docker'],
                'posted_by': users['hr_damir'], 'honesty_score': 82,
            },
            {
                'title': 'Senior Backend Engineer',
                'company': 'CloudSys', 'location': 'Астана', 'level': 'senior',
                'salary_min': 1500000, 'salary_max': 2500000,
                'experience_years': 5, 'is_remote': True, 'training_provided': False,
                'description': 'Ведущий backend разработчик для архитектуры микросервисов.',
                'requirements_text': '5+ лет, опыт с Go/Python, микросервисы, Docker, Kubernetes, AWS.',
                'tech_stack': ['Go', 'Python', 'Docker', 'Kubernetes', 'AWS', 'PostgreSQL', 'Redis'],
                'posted_by': users['hr_damir'], 'honesty_score': 78,
            },
            {
                'title': 'Senior Fullstack Developer',
                'company': 'WebStudio', 'location': 'Удалённо', 'level': 'senior',
                'salary_min': 1800000, 'salary_max': 3000000,
                'experience_years': 5, 'is_remote': True, 'training_provided': False,
                'description': 'Full-stack позиция для опытного разработчика.',
                'requirements_text': 'React, Node.js, Python, PostgreSQL, Docker. 5+ лет опыта.',
                'tech_stack': ['React', 'Node.js', 'Python', 'PostgreSQL', 'Docker'],
                'posted_by': users['hr_asel'], 'honesty_score': 75,
            },
            {
                'title': 'DevOps Engineer',
                'company': 'CloudSys', 'location': 'Астана', 'level': 'mid',
                'salary_min': 900000, 'salary_max': 1500000,
                'experience_years': 3, 'is_remote': True, 'training_provided': False,
                'description': 'DevOps инженер для настройки CI/CD и облачной инфраструктуры.',
                'requirements_text': 'Docker, Kubernetes, CI/CD, Linux, AWS или GCP. Terraform желательно.',
                'tech_stack': ['Docker', 'Kubernetes', 'AWS', 'Terraform', 'Linux'],
                'posted_by': users['hr_damir'], 'honesty_score': 80,
            },
        ]
        for d in data:
            job, created = Job.objects.get_or_create(
                title=d['title'], company=d['company'],
                defaults=d,
            )
            if created:
                self.stdout.write(f'  + Job: {job.title} ({job.level})')
            jobs[d['title']] = job
        return jobs

    def _create_tags(self, jobs):
        tag_names = ['Python', 'JavaScript', 'React', 'Django', 'Docker', 'Go', 'Java', 'AWS', 'DevOps', 'Remote']
        for name in tag_names:
            JobTag.objects.get_or_create(name=name)

    def _create_tests(self):
        tests = {}
        data = [
            {
                'title': 'Python Basics',
                'language': 'python', 'difficulty': 'easy',
                'description': 'Базовые вопросы по Python: типы данных, циклы, функции.',
                'questions': [
                    ('Что вернёт type([])?', "<class 'list'>", "<class 'tuple'>", "<class 'dict'>", "<class 'set'>", 'a'),
                    ('Как создать словарь в Python?', '{}', '[]', '()', '<>', 'a'),
                    ('Что делает len()?', 'Возвращает длину', 'Сортирует', 'Удаляет', 'Копирует', 'a'),
                    ('Какой оператор используется для возведения в степень?', '**', '^', '//', '%%', 'a'),
                    ('Что такое list comprehension?', 'Сокращённое создание списка', 'Тип данных', 'Метод сортировки', 'Цикл', 'a'),
                ],
            },
            {
                'title': 'Django Fundamentals',
                'language': 'python', 'difficulty': 'medium',
                'description': 'Вопросы по Django ORM, views, и шаблонам.',
                'questions': [
                    ('Что такое ORM в Django?', 'Object-Relational Mapping', 'Object Resource Manager', 'Open Request Model', 'Output Render Module', 'a'),
                    ('Какой метод HTTP используется для создания ресурса?', 'POST', 'GET', 'DELETE', 'OPTIONS', 'a'),
                    ('Что делает migrate?', 'Применяет миграции к БД', 'Создаёт миграции', 'Удаляет таблицы', 'Создаёт суперпользователя', 'a'),
                    ('Что такое middleware?', 'Промежуточный обработчик запросов', 'Шаблон', 'Модель', 'Тест', 'a'),
                ],
            },
            {
                'title': 'JavaScript Basics',
                'language': 'javascript', 'difficulty': 'easy',
                'description': 'Основы JavaScript: переменные, функции, DOM.',
                'questions': [
                    ('Чем let отличается от var?', 'Блочная область видимости', 'Нет отличий', 'let быстрее', 'var новее', 'a'),
                    ('Что такое === в JavaScript?', 'Строгое сравнение', 'Присваивание', 'Нестрогое сравнение', 'Ошибка синтаксиса', 'a'),
                    ('Что возвращает typeof null?', 'object', 'null', 'undefined', 'boolean', 'a'),
                    ('Как объявить стрелочную функцию?', 'const f = () => {}', 'function f() {}', 'def f():', 'fn f() {}', 'a'),
                    ('Что делает Array.map()?', 'Создаёт новый массив', 'Фильтрует массив', 'Сортирует', 'Удаляет элементы', 'a'),
                ],
            },
            {
                'title': 'React Hooks',
                'language': 'react', 'difficulty': 'medium',
                'description': 'Тест по React хукам: useState, useEffect, useContext.',
                'questions': [
                    ('Что возвращает useState?', 'Массив [значение, setter]', 'Объект', 'Строку', 'Число', 'a'),
                    ('Когда вызывается useEffect?', 'После рендера', 'До рендера', 'При монтировании только', 'Никогда', 'a'),
                    ('Для чего нужен useContext?', 'Доступ к контексту', 'Управление состоянием', 'Роутинг', 'HTTP запросы', 'a'),
                ],
            },
            {
                'title': 'SQL Fundamentals',
                'language': 'general', 'difficulty': 'easy',
                'description': 'Основы SQL: SELECT, JOIN, WHERE, GROUP BY.',
                'questions': [
                    ('Какой оператор используется для выборки данных?', 'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'a'),
                    ('Что делает JOIN?', 'Объединяет таблицы', 'Удаляет записи', 'Создаёт таблицу', 'Сортирует', 'a'),
                    ('Для чего GROUP BY?', 'Группировка результатов', 'Сортировка', 'Фильтрация', 'Объединение', 'a'),
                    ('Что делает WHERE?', 'Фильтрует строки', 'Группирует', 'Сортирует', 'Объединяет таблицы', 'a'),
                ],
            },
            {
                'title': 'Docker & DevOps',
                'language': 'general', 'difficulty': 'hard',
                'description': 'Продвинутые вопросы по Docker, CI/CD и инфраструктуре.',
                'questions': [
                    ('Что такое Docker контейнер?', 'Изолированная среда выполнения', 'Виртуальная машина', 'Операционная система', 'Язык программирования', 'a'),
                    ('Для чего docker-compose?', 'Оркестрация нескольких контейнеров', 'Сборка образов', 'Мониторинг', 'Тестирование', 'a'),
                    ('Что такое CI/CD?', 'Непрерывная интеграция и доставка', 'Cloud Infrastructure', 'Container Integration', 'Code Inspection', 'a'),
                ],
            },
        ]
        for t in data:
            test, created = SkillTest.objects.get_or_create(
                title=t['title'],
                defaults={
                    'language': t['language'],
                    'difficulty': t['difficulty'],
                    'description': t['description'],
                },
            )
            if created:
                for i, (text, a, b, c, d, correct) in enumerate(t['questions']):
                    Question.objects.create(
                        test=test, text=text, order=i + 1,
                        question_type='quiz',
                        option_a=a, option_b=b, option_c=c, option_d=d,
                        correct_answer=correct,
                    )
                self.stdout.write(f'  + Test: {test.title} ({len(t["questions"])} questions)')
            tests[t['title']] = test
        return tests

    def _create_applications(self, users, jobs):
        apps = {}
        data = [
            ('azamat', 'Junior Python Developer', 'Здравствуйте! Я выпускник АУЭС, хочу начать карьеру Python разработчика. Знаю Django и SQL.', 'pending'),
            ('azamat', 'Junior JavaScript Developer', 'Интересуюсь Full-stack разработкой, хотел бы попробовать Node.js.', 'pending'),
            ('dana', 'Junior Frontend Developer', 'Привет! Я учусь фронтенд-разработке и хочу получить первый опыт.', 'accepted'),
            ('dana', 'Mid React Developer', 'Хочу расти как React разработчик!', 'rejected'),
            ('timur', 'Mid Django Developer', 'У меня 2 года опыта с Django, готов к новым проектам.', 'accepted'),
            ('timur', 'Senior Backend Engineer', 'Хочу расти дальше в backend направлении.', 'pending'),
            ('aliya', 'Mid Java Developer', 'Java разработчик с опытом Spring Boot. Ищу стабильную компанию.', 'accepted'),
            ('nursultan', 'Junior Python Developer', 'Начинающий разработчик, очень хочу учиться!', 'pending'),
            ('nursultan', 'Junior Frontend Developer', 'Также интересуюсь фронтендом.', 'pending'),
            ('aigul', 'Junior JavaScript Developer', 'Хочу стать fullstack разработчиком, начинаю с JS.', 'accepted'),
            ('marat', 'Senior Backend Engineer', 'Senior backend инженер с 6+ лет опыта.', 'accepted'),
            ('marat', 'DevOps Engineer', 'Имею опыт с Kubernetes и AWS.', 'pending'),
        ]
        for username, job_title, cover, app_status in data:
            user = users.get(username)
            job = jobs.get(job_title)
            if not user or not job:
                continue
            app, created = Application.objects.get_or_create(
                applicant=user, job=job,
                defaults={'cover_letter': cover, 'status': app_status},
            )
            if created:
                if app_status != 'pending':
                    app.status = app_status
                    app.save()
                self.stdout.write(f'  + Application: {username} -> {job_title} [{app_status}]')
            apps[(username, job_title)] = app
        return apps

    def _create_messages(self, apps, users):
        conversations = [
            (('dana', 'Junior Frontend Developer'), [
                ('hr_asel', 'Здравствуйте, Dana! Мы рассмотрели вашу заявку и хотим пригласить на собеседование.'),
                ('dana', 'Здравствуйте! Спасибо большое, я очень рада! Когда удобно?'),
                ('hr_asel', 'Предлагаю в среду в 15:00 по Zoom. Ссылку пришлю за час до встречи.'),
                ('dana', 'Отлично, буду готова! Спасибо!'),
            ]),
            (('timur', 'Mid Django Developer'), [
                ('hr_ivan', 'Тимур, добро пожаловать в команду! Готовим оффер.'),
                ('timur', 'Спасибо! Когда можно начать?'),
                ('hr_ivan', 'С 1 числа следующего месяца. Пришлю документы на почту.'),
            ]),
            (('azamat', 'Junior Python Developer'), [
                ('hr_ivan', 'Azamat, спасибо за заявку! Расскажите подробнее о своих проектах.'),
                ('azamat', 'Я делал дипломный проект — платформу для поиска работы на Django + Flutter.'),
                ('hr_ivan', 'Звучит интересно! Можете показать GitHub?'),
            ]),
            (('marat', 'Senior Backend Engineer'), [
                ('hr_damir', 'Марат, впечатляющий опыт! Давайте обсудим условия.'),
                ('marat', 'Конечно, буду рад. Какой формат собеседования?'),
                ('hr_damir', 'Два этапа: техническое интервью и system design. По 1 часу каждое.'),
                ('marat', 'Подходит. Когда начнём?'),
                ('hr_damir', 'Предлагаю в понедельник в 11:00.'),
            ]),
        ]
        count = 0
        for (username, job_title), messages in conversations:
            app = apps.get((username, job_title))
            if not app:
                continue
            if app.messages.exists():
                continue
            for sender_name, text in messages:
                sender = users.get(sender_name)
                if sender:
                    Message.objects.create(application=app, sender=sender, text=text)
                    count += 1
        if count:
            self.stdout.write(f'  + Messages: {count} created')

    def _create_test_results(self, users, tests):
        results = [
            ('azamat', 'Python Basics', 4, 5, 'passed'),
            ('azamat', 'Django Fundamentals', 3, 4, 'passed'),
            ('azamat', 'SQL Fundamentals', 3, 4, 'passed'),
            ('dana', 'JavaScript Basics', 5, 5, 'passed'),
            ('dana', 'React Hooks', 2, 3, 'passed'),
            ('timur', 'Python Basics', 5, 5, 'passed'),
            ('timur', 'Django Fundamentals', 4, 4, 'passed'),
            ('timur', 'Docker & DevOps', 2, 3, 'passed'),
            ('nursultan', 'Python Basics', 2, 5, 'failed'),
            ('aigul', 'JavaScript Basics', 4, 5, 'passed'),
            ('marat', 'Python Basics', 5, 5, 'passed'),
            ('marat', 'Docker & DevOps', 3, 3, 'passed'),
        ]
        count = 0
        for username, test_title, score, max_score, result_status in results:
            user = users.get(username)
            test = tests.get(test_title)
            if not user or not test:
                continue
            _, created = TestResult.objects.get_or_create(
                user=user, test=test,
                defaults={
                    'score': score, 'max_score': max_score,
                    'status': result_status,
                    'completed_at': timezone.now(),
                },
            )
            if created:
                count += 1
        if count:
            self.stdout.write(f'  + Test results: {count} created')

    def _create_favorites(self, users, jobs):
        favs = [
            ('azamat', 'Junior Python Developer'),
            ('azamat', 'Junior JavaScript Developer'),
            ('azamat', 'Mid Django Developer'),
            ('dana', 'Junior Frontend Developer'),
            ('dana', 'Mid React Developer'),
            ('timur', 'Senior Backend Engineer'),
            ('nursultan', 'Junior Python Developer'),
            ('aigul', 'Junior JavaScript Developer'),
        ]
        count = 0
        for username, job_title in favs:
            user = users.get(username)
            job = jobs.get(job_title)
            if not user or not job:
                continue
            _, created = Favorite.objects.get_or_create(user=user, job=job)
            if created:
                count += 1
        if count:
            self.stdout.write(f'  + Favorites: {count} created')
