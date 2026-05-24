from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from jobs.models import Job
from tests_system.models import SkillTest, Question
from applications.models import Application
from analytics.models import Favorite


class Command(BaseCommand):
    help = 'Seed database with demo data: users, jobs, tests, applications'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Delete existing data before seeding')

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting data...')
            Answer = __import__('tests_system.models', fromlist=['Answer']).Answer
            TestResult = __import__('tests_system.models', fromlist=['TestResult']).TestResult
            Favorite.objects.all().delete()
            Application.objects.all().delete()
            Answer.objects.all().delete()
            TestResult.objects.all().delete()
            Question.objects.all().delete()
            SkillTest.objects.all().delete()
            Job.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Seeding database...')
        self._create_users()
        self._create_jobs()
        self._create_tests()
        self._create_applications()
        self.stdout.write(self.style.SUCCESS('Done!'))

    def _make_user(self, username, email, password, role, **profile_kwargs):
        if User.objects.filter(username=username).exists():
            return User.objects.get(username=username)
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, role=role, **profile_kwargs)
        return user

    def _create_users(self):
        self.stdout.write('  Creating users...')

        # --- Applicants (12) ---
        self._make_user('alice', 'alice@example.com', 'password123', 'applicant',
            level='junior', bio='Начинающий Python-разработчик, учусь в университете. Люблю backend.',
            skills=['Python', 'Django', 'Git', 'SQL', 'HTML', 'CSS'],
            portfolio_url='https://alice-dev.example.com',
            github_url='https://github.com/alice-dev')

        self._make_user('bob', 'bob@example.com', 'password123', 'applicant',
            level='junior', bio='Фронтенд-разработчик, 6 месяцев опыта с React. Ищу первую работу.',
            skills=['JavaScript', 'React', 'HTML', 'CSS', 'TypeScript', 'Git'],
            github_url='https://github.com/bob-frontend')

        self._make_user('charlie', 'charlie@example.com', 'password123', 'applicant',
            level='mid', bio='Fullstack-разработчик с 2 годами опыта. Python + React.',
            skills=['Python', 'Django', 'JavaScript', 'React', 'PostgreSQL', 'Docker', 'Git', 'REST API', 'Redis'],
            portfolio_url='https://charlie.dev',
            github_url='https://github.com/charlie-fs')

        self._make_user('diana', 'diana@example.com', 'password123', 'applicant',
            level='junior', bio='Java-разработчик, закончила курсы. Хочу в enterprise-разработку.',
            skills=['Java', 'Spring', 'SQL', 'Git', 'Maven'])

        self._make_user('erik', 'erik@example.com', 'password123', 'applicant',
            level='senior', bio='10 лет опыта в backend. Python, Go, микросервисы, облака.',
            skills=['Python', 'Go', 'Kubernetes', 'Docker', 'AWS', 'PostgreSQL', 'Redis', 'Kafka', 'CI/CD', 'Terraform', 'gRPC'],
            portfolio_url='https://erik-senior.dev',
            github_url='https://github.com/erik-arch')

        self._make_user('fatima', 'fatima@example.com', 'password123', 'applicant',
            level='junior', bio='Data Science студентка. Интересуюсь ML и аналитикой данных.',
            skills=['Python', 'Pandas', 'NumPy', 'SQL', 'Jupyter', 'Matplotlib', 'Git'],
            github_url='https://github.com/fatima-ds')

        self._make_user('george', 'george@example.com', 'password123', 'applicant',
            level='mid', bio='DevOps-инженер, 3 года опыта. Автоматизирую всё.',
            skills=['Docker', 'Kubernetes', 'Linux', 'CI/CD', 'Terraform', 'AWS', 'Python', 'Bash', 'Ansible', 'Prometheus'])

        self._make_user('hana', 'hana@example.com', 'password123', 'applicant',
            level='junior', bio='QA инженер, перехожу в разработку. Знаю автотесты.',
            skills=['Python', 'Selenium', 'Git', 'SQL', 'Postman', 'Jira'])

        self._make_user('ivan', 'ivan@example.com', 'password123', 'applicant',
            level='mid', bio='Mobile-разработчик, React Native + немного backend.',
            skills=['JavaScript', 'React', 'React Native', 'TypeScript', 'Node.js', 'Firebase', 'Git'])

        self._make_user('julia', 'julia@example.com', 'password123', 'applicant',
            level='junior', bio='Выпускница bootcamp по web-разработке. Готова к первой работе!',
            skills=['HTML', 'CSS', 'JavaScript', 'React', 'Git', 'Figma'])

        self._make_user('marat', 'marat@example.com', 'password123', 'applicant',
            level='junior', bio='Студент 3 курса. Учу Python и Django. Хочу стажировку.',
            skills=['Python', 'HTML', 'CSS', 'Git', 'SQL'],
            github_url='https://github.com/marat-student')

        self._make_user('nastya', 'nastya@example.com', 'password123', 'applicant',
            level='mid', bio='2 года в frontend. Vue.js, React. Хочу в продуктовую компанию.',
            skills=['JavaScript', 'Vue.js', 'React', 'TypeScript', 'HTML', 'CSS', 'Git', 'Webpack', 'REST API'])

        # --- HR Managers (3) ---
        self._make_user('hr_techcorp', 'hr@techcorp.kz', 'password123', 'hr',
            company_name='TechCorp Kazakhstan',
            company_description='Крупная IT-компания, 500+ сотрудников. Разрабатываем финтех решения для банков и страховых.')

        self._make_user('hr_startupx', 'hr@startupx.io', 'password123', 'hr',
            company_name='StartupX',
            company_description='Быстрорастущий стартап в сфере EdTech. Команда из 30 человек.')

        self._make_user('hr_dataflow', 'hr@dataflow.kz', 'password123', 'hr',
            company_name='DataFlow Analytics',
            company_description='Компания по анализу данных и ML-решениям для бизнеса.')

        self.stdout.write(f'    Users: {User.objects.count()}')

    def _create_jobs(self):
        self.stdout.write('  Creating jobs...')
        if Job.objects.exists():
            self.stdout.write('    Jobs already exist, skipping.')
            return

        hr_tc = User.objects.get(username='hr_techcorp')
        hr_sx = User.objects.get(username='hr_startupx')
        hr_df = User.objects.get(username='hr_dataflow')

        jobs_data = [
            # ============================================================
            # TechCorp Kazakhstan — 12 вакансий (основная компания)
            # ============================================================
            {
                'title': 'Junior Python Developer',
                'description': 'Ищем начинающего Python-разработчика в команду backend. Вы будете работать над API для финтех-продуктов, писать тесты и участвовать в code review. Ментор поможет вырасти до Middle за год.',
                'company': 'TechCorp Kazakhstan', 'location': 'Алматы',
                'salary_min': 250000, 'salary_max': 400000, 'level': 'junior',
                'requirements_text': 'Базовое знание Python. Понимание HTTP, REST API. Знакомство с SQL. Основы Git. Желание учиться.',
                'training_provided': True, 'experience_years': 0, 'is_remote': False,
                'tech_stack': ['Python', 'Django', 'PostgreSQL', 'Git', 'Docker'],
                'posted_by': hr_tc,
            },
            {
                'title': 'Junior Frontend Developer (React)',
                'description': 'Присоединяйтесь к frontend-команде! Будете верстать интерфейсы, работать с API, участвовать в дизайн-ревью. Используем React + TypeScript.',
                'company': 'TechCorp Kazakhstan', 'location': 'Алматы',
                'salary_min': 230000, 'salary_max': 380000, 'level': 'junior',
                'requirements_text': 'HTML, CSS на уверенном уровне. JavaScript (ES6+). Базовый React. Адаптивная вёрстка. Git.',
                'training_provided': True, 'experience_years': 0, 'is_remote': True,
                'tech_stack': ['React', 'TypeScript', 'HTML', 'CSS', 'Git'],
                'posted_by': hr_tc,
            },
            {
                'title': 'Middle Python Developer',
                'description': 'Backend-разработчик в команду платёжных систем. Высоконагруженный проект, микросервисы, работа с финансовыми данными.',
                'company': 'TechCorp Kazakhstan', 'location': 'Алматы',
                'salary_min': 600000, 'salary_max': 900000, 'level': 'mid',
                'requirements_text': 'Python 2+ года. Django/FastAPI. PostgreSQL, Redis. Docker. REST API проектирование. Понимание SOLID, паттернов. Опыт с очередями (Celery/RabbitMQ).',
                'training_provided': False, 'experience_years': 2, 'is_remote': False,
                'tech_stack': ['Python', 'Django', 'FastAPI', 'PostgreSQL', 'Redis', 'Docker', 'Celery', 'RabbitMQ'],
                'posted_by': hr_tc,
            },
            {
                'title': 'Senior Backend Developer (Python)',
                'description': 'Технический лидер backend-направления. Проектирование архитектуры, менторство, оптимизация производительности критичных сервисов.',
                'company': 'TechCorp Kazakhstan', 'location': 'Алматы',
                'salary_min': 1200000, 'salary_max': 1800000, 'level': 'senior',
                'requirements_text': 'Python 5+ лет. Микросервисная архитектура. Kubernetes, Docker. PostgreSQL оптимизация. Опыт лидирования команды. CI/CD. Мониторинг.',
                'training_provided': False, 'experience_years': 5, 'is_remote': True,
                'tech_stack': ['Python', 'Django', 'FastAPI', 'Kubernetes', 'Docker', 'PostgreSQL', 'Redis', 'Kafka', 'AWS'],
                'posted_by': hr_tc,
            },
            {
                'title': 'Junior QA Engineer',
                'description': 'Тестировщик в финтех-команду. Будете писать тест-кейсы, находить баги, помогать с автоматизацией. Обучим всему.',
                'company': 'TechCorp Kazakhstan', 'location': 'Алматы',
                'salary_min': 200000, 'salary_max': 320000, 'level': 'junior',
                'requirements_text': 'Понимание тестирования (виды, уровни). SQL базовый. Postman. Внимательность к деталям.',
                'training_provided': True, 'experience_years': 0, 'is_remote': False,
                'tech_stack': ['Postman', 'SQL', 'Jira', 'Python', 'Selenium'],
                'posted_by': hr_tc,
            },
            {
                'title': 'Middle Frontend Developer (React)',
                'description': 'Разработка UI для банковских продуктов. Дизайн-система, компонентная архитектура, работа с бизнес-логикой.',
                'company': 'TechCorp Kazakhstan', 'location': 'Алматы',
                'salary_min': 550000, 'salary_max': 850000, 'level': 'mid',
                'requirements_text': 'React 2+ года. TypeScript. Redux/MobX. REST API. Тестирование (Jest). Адаптивная вёрстка. Git.',
                'training_provided': False, 'experience_years': 2, 'is_remote': True,
                'tech_stack': ['React', 'TypeScript', 'Redux', 'Jest', 'HTML', 'CSS', 'Git', 'Webpack'],
                'posted_by': hr_tc,
            },
            {
                'title': 'DevOps Engineer',
                'description': 'Настройка и поддержка инфраструктуры для финтех-продуктов. CI/CD, мониторинг, автоматизация.',
                'company': 'TechCorp Kazakhstan', 'location': 'Алматы',
                'salary_min': 700000, 'salary_max': 1100000, 'level': 'mid',
                'requirements_text': 'Linux. Docker, Kubernetes. Terraform. CI/CD (GitLab CI). AWS или GCP. Мониторинг (Prometheus, Grafana). Python/Bash.',
                'training_provided': False, 'experience_years': 2, 'is_remote': True,
                'tech_stack': ['Docker', 'Kubernetes', 'Terraform', 'AWS', 'Linux', 'Prometheus', 'Grafana', 'Python'],
                'posted_by': hr_tc,
            },
            {
                'title': 'Junior Java Developer',
                'description': 'Java-разработка банковских микросервисов. Стабильная компания, белая зарплата, ДМС. Обучение в первый месяц.',
                'company': 'TechCorp Kazakhstan', 'location': 'Алматы',
                'salary_min': 280000, 'salary_max': 420000, 'level': 'junior',
                'requirements_text': 'Java базовый. ООП. SQL. Git. Желание работать в финтехе.',
                'training_provided': True, 'experience_years': 0, 'is_remote': False,
                'tech_stack': ['Java', 'Spring', 'PostgreSQL', 'Git', 'Maven'],
                'posted_by': hr_tc,
            },
            {
                'title': 'Data Analyst',
                'description': 'Аналитик данных для команды бизнес-аналитики. Дашборды, отчёты, поиск инсайтов в данных транзакций.',
                'company': 'TechCorp Kazakhstan', 'location': 'Алматы',
                'salary_min': 350000, 'salary_max': 550000, 'level': 'mid',
                'requirements_text': 'SQL продвинутый. Python (Pandas). BI инструменты (Tableau/Power BI). Понимание статистики. Excel продвинутый.',
                'training_provided': False, 'experience_years': 1, 'is_remote': False,
                'tech_stack': ['SQL', 'Python', 'Pandas', 'Tableau', 'Excel'],
                'posted_by': hr_tc,
            },
            {
                'title': 'Junior Mobile Developer (Flutter)',
                'description': 'Разработка мобильного приложения для клиентов банка. Flutter, Dart, интеграция с REST API.',
                'company': 'TechCorp Kazakhstan', 'location': 'Алматы',
                'salary_min': 250000, 'salary_max': 400000, 'level': 'junior',
                'requirements_text': 'Dart/Flutter базовый. Понимание мобильной разработки. REST API. Git.',
                'training_provided': True, 'experience_years': 0, 'is_remote': False,
                'tech_stack': ['Flutter', 'Dart', 'REST API', 'Git', 'Firebase'],
                'posted_by': hr_tc,
            },
            # TechCorp — DISHONEST: стажёр с завышенными требованиями
            {
                'title': 'Стажёр Frontend-разработчик',
                'description': 'Стажировка с возможностью трудоустройства. 3 месяца обучения.',
                'company': 'TechCorp Kazakhstan', 'location': 'Алматы',
                'salary_min': 100000, 'salary_max': 180000, 'level': 'junior',
                'requirements_text': 'React, TypeScript, Redux, Next.js, GraphQL, Webpack, Docker, CI/CD, тестирование (Jest, Cypress), 1 год коммерческого опыта.',
                'training_provided': True, 'experience_years': 1, 'is_remote': False,
                'tech_stack': ['React', 'TypeScript', 'Redux', 'Next.js', 'GraphQL', 'Webpack', 'Docker', 'Jest', 'Cypress'],
                'posted_by': hr_tc,
            },
            # TechCorp — DISHONEST: junior с senior-требованиями
            {
                'title': 'Junior Backend Developer (Node.js)',
                'description': 'Начальная позиция backend-разработчика. Работа с микросервисами.',
                'company': 'TechCorp Kazakhstan', 'location': 'Алматы',
                'salary_min': 220000, 'salary_max': 350000, 'level': 'junior',
                'requirements_text': 'Node.js, TypeScript, PostgreSQL, MongoDB, Redis, Docker, Kubernetes, CI/CD, микросервисы, GraphQL, AWS, очереди сообщений (RabbitMQ/Kafka), 2 года опыта.',
                'training_provided': False, 'experience_years': 2, 'is_remote': False,
                'tech_stack': ['Node.js', 'TypeScript', 'PostgreSQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes', 'AWS', 'GraphQL'],
                'posted_by': hr_tc,
            },

            # ============================================================
            # StartupX — 4 вакансии
            # ============================================================
            {
                'title': 'Fullstack Developer (Junior+)',
                'description': 'Стартап в EdTech ищет разработчика, который не боится и frontend, и backend. Маленькая команда — много свободы и ответственности.',
                'company': 'StartupX', 'location': 'Астана',
                'salary_min': 300000, 'salary_max': 500000, 'level': 'junior',
                'requirements_text': 'JavaScript или Python. Базовый React или Vue. Понимание REST API. SQL. Git. Умение разбираться в чужом коде.',
                'training_provided': True, 'experience_years': 0, 'is_remote': True,
                'tech_stack': ['Python', 'Django', 'React', 'PostgreSQL', 'Git'],
                'posted_by': hr_sx,
            },
            {
                'title': 'Mobile Developer (React Native)',
                'description': 'Разрабатываем мобильное приложение для онлайн-обучения. Нужен разработчик с опытом React Native.',
                'company': 'StartupX', 'location': 'Астана',
                'salary_min': 450000, 'salary_max': 700000, 'level': 'mid',
                'requirements_text': 'React Native 1+ год. JavaScript/TypeScript. REST API интеграция. Публикация в App Store/Google Play.',
                'training_provided': False, 'experience_years': 1, 'is_remote': True,
                'tech_stack': ['React Native', 'TypeScript', 'JavaScript', 'Firebase', 'Git'],
                'posted_by': hr_sx,
            },
            {
                'title': 'Junior Python Developer (Remote)',
                'description': 'Полностью удалённая работа! Пишем backend для EdTech-платформы. Гибкий график.',
                'company': 'StartupX', 'location': 'Удалённо',
                'salary_min': 270000, 'salary_max': 420000, 'level': 'junior',
                'requirements_text': 'Python. Базовый Django. Git. Желание учиться быстро.',
                'training_provided': True, 'experience_years': 0, 'is_remote': True,
                'tech_stack': ['Python', 'Django', 'PostgreSQL', 'Git', 'Docker'],
                'posted_by': hr_sx,
            },
            {
                'title': 'UI/UX Designer',
                'description': 'Дизайнер для EdTech-продукта. Прототипирование, дизайн-система, пользовательские исследования.',
                'company': 'StartupX', 'location': 'Астана',
                'salary_min': 350000, 'salary_max': 600000, 'level': 'mid',
                'requirements_text': 'Figma. Опыт дизайна мобильных приложений. Понимание UX. Портфолио.',
                'training_provided': False, 'experience_years': 1, 'is_remote': True,
                'tech_stack': ['Figma', 'Sketch', 'Adobe XD'],
                'posted_by': hr_sx,
            },

            # ============================================================
            # DataFlow Analytics — 4 вакансии
            # ============================================================
            # DISHONEST: junior с senior-требованиями
            {
                'title': 'Junior Data Analyst',
                'description': 'Начальная позиция аналитика данных. Работа с отчётами, дашбордами.',
                'company': 'DataFlow Analytics', 'location': 'Алматы',
                'salary_min': 200000, 'salary_max': 350000, 'level': 'junior',
                'requirements_text': 'Python, Pandas, NumPy, SQL, Machine Learning (scikit-learn, XGBoost), Deep Learning (TensorFlow, PyTorch), Apache Spark, Airflow, Docker, Kubernetes, 3 года опыта в анализе данных.',
                'training_provided': False, 'experience_years': 3, 'is_remote': False,
                'tech_stack': ['Python', 'Pandas', 'SQL', 'TensorFlow', 'PyTorch', 'Spark', 'Airflow', 'Docker', 'Kubernetes'],
                'posted_by': hr_df,
            },
            {
                'title': 'Middle Data Engineer',
                'description': 'Строим пайплайны данных для крупных клиентов. Работа с большими объёмами, ETL процессы.',
                'company': 'DataFlow Analytics', 'location': 'Алматы',
                'salary_min': 600000, 'salary_max': 1000000, 'level': 'mid',
                'requirements_text': 'Python, SQL продвинутый. Apache Spark/Flink. Airflow. AWS или GCP. Docker. 2+ года с данными.',
                'training_provided': False, 'experience_years': 2, 'is_remote': True,
                'tech_stack': ['Python', 'SQL', 'Spark', 'Airflow', 'AWS', 'Docker', 'PostgreSQL'],
                'posted_by': hr_df,
            },
            {
                'title': 'Senior ML Engineer',
                'description': 'Лидирование ML-направления. Проектирование моделей, MLOps, менторство.',
                'company': 'DataFlow Analytics', 'location': 'Алматы',
                'salary_min': 1200000, 'salary_max': 2000000, 'level': 'senior',
                'requirements_text': 'Python, ML/DL 5+ лет. PyTorch/TensorFlow. MLflow, Kubeflow. Docker, Kubernetes. AWS SageMaker.',
                'training_provided': False, 'experience_years': 5, 'is_remote': True,
                'tech_stack': ['Python', 'PyTorch', 'TensorFlow', 'MLflow', 'Kubernetes', 'Docker', 'AWS'],
                'posted_by': hr_df,
            },
            {
                'title': 'Junior Python Developer',
                'description': 'Разработка ETL-пайплайнов и API для клиентов. Python + SQL.',
                'company': 'DataFlow Analytics', 'location': 'Алматы',
                'salary_min': 230000, 'salary_max': 380000, 'level': 'junior',
                'requirements_text': 'Python. SQL. Базовый Pandas. Git. Желание работать с данными.',
                'training_provided': True, 'experience_years': 0, 'is_remote': False,
                'tech_stack': ['Python', 'SQL', 'Pandas', 'Git', 'Docker'],
                'posted_by': hr_df,
            },
        ]

        for jd in jobs_data:
            Job.objects.create(**jd)

        self.stdout.write(f'    Jobs: {Job.objects.count()}')

    def _create_tests(self):
        self.stdout.write('  Creating tests...')
        if SkillTest.objects.exists():
            self.stdout.write('    Tests already exist, skipping.')
            return

        # ===== Python Basics =====
        t1 = SkillTest.objects.create(
            title='Python: Основы', language='python', difficulty='easy',
            description='Базовые конструкции Python: типы данных, циклы, функции, строки.')
        for i, q in enumerate([
            ('Какой тип данных вернёт выражение type(3.14)?', 'int', 'float', 'str', 'decimal', 'b'),
            ('Что выведет len("Hello")?', '4', '5', '6', 'Ошибку', 'b'),
            ('Как создать пустой словарь?', 'dict()', '{}', 'Оба варианта верны', 'new dict()', 'c'),
            ('Что делает метод .append() у списка?', 'Удаляет элемент', 'Добавляет в конец', 'Сортирует', 'Копирует список', 'b'),
            ('Какой оператор используется для проверки вхождения элемента?', 'has', 'contains', 'in', 'exists', 'c'),
            ('Что вернёт bool("")?', 'True', 'False', 'None', 'Ошибку', 'b'),
            ('Как получить последний элемент списка lst?', 'lst[0]', 'lst[-1]', 'lst.last()', 'lst.end()', 'b'),
            ('Что такое list comprehension?', 'Импорт списков', 'Способ создания списка в одну строку', 'Сортировка', 'Метод списка', 'b'),
        ], 1):
            Question.objects.create(test=t1, question_type='quiz', text=q[0],
                option_a=q[1], option_b=q[2], option_c=q[3], option_d=q[4],
                correct_answer=q[5], order=i)

        # ===== Python Advanced =====
        t2 = SkillTest.objects.create(
            title='Python: Продвинутый', language='python', difficulty='medium',
            description='Декораторы, генераторы, ООП, модули, исключения.')
        for i, q in enumerate([
            ('Что такое декоратор в Python?', 'Класс для UI', 'Функция, оборачивающая другую функцию', 'Тип данных', 'Модуль стандартной библиотеки', 'b'),
            ('Что делает ключевое слово yield?', 'Завершает функцию', 'Создаёт генератор', 'Импортирует модуль', 'Вызывает исключение', 'b'),
            ('Какой метод вызывается при создании объекта класса?', '__create__', '__new__ и __init__', '__start__', '__build__', 'b'),
            ('Что такое *args в определении функции?', 'Именованные аргументы', 'Кортеж позиционных аргументов', 'Список', 'Словарь', 'b'),
            ('Как правильно обработать исключение?', 'catch Exception', 'try/except', 'handle Error', 'error/resolve', 'b'),
            ('Что делает @staticmethod?', 'Кэширует метод', 'Делает метод классовым', 'Убирает self из аргументов', 'Делает метод приватным', 'c'),
            ('Что такое GIL?', 'Графическая библиотека', 'Global Interpreter Lock', 'Генератор', 'Модуль ввода-вывода', 'b'),
            ('Как создать виртуальное окружение?', 'pip create env', 'python -m venv myenv', 'virtualenv --new', 'python env init', 'b'),
            ('Что вернёт isinstance(True, int)?', 'True', 'False', 'Ошибку', 'None', 'a'),
            ('Для чего используется __slots__?', 'Для слотов памяти', 'Ограничение атрибутов класса', 'Для многопоточности', 'Для сортировки', 'b'),
        ], 1):
            Question.objects.create(test=t2, question_type='quiz', text=q[0],
                option_a=q[1], option_b=q[2], option_c=q[3], option_d=q[4],
                correct_answer=q[5], order=i)

        # ===== Django =====
        t3 = SkillTest.objects.create(
            title='Django Framework', language='python', difficulty='medium',
            description='Модели, views, ORM, шаблоны, формы, middleware.')
        for i, q in enumerate([
            ('Какая команда создаёт миграции в Django?', 'python manage.py migrate', 'python manage.py makemigrations', 'python manage.py createdb', 'django migrate', 'b'),
            ('Что такое ORM?', 'Система кэширования', 'Маппинг объектов на таблицы БД', 'Шаблонизатор', 'Менеджер пакетов', 'b'),
            ('Какой класс используется для REST API views в DRF?', 'TemplateView', 'APIView', 'FormView', 'HttpView', 'b'),
            ('Что делает select_related()?', 'Выбирает поля', 'Делает JOIN для FK', 'Фильтрует queryset', 'Сортирует результат', 'b'),
            ('Как определить URL-маршрут в Django?', 'route()', 'path()', 'url_map()', 'define_url()', 'b'),
            ('Что такое middleware в Django?', 'База данных', 'Слой обработки запросов/ответов', 'Шаблонизатор', 'Админ-панель', 'b'),
            ('Какой метод возвращает один объект или 404?', 'get_or_none()', 'get_object_or_404()', 'find_one()', 'fetch()', 'b'),
            ('Что такое сериализатор в DRF?', 'Шифрование данных', 'Конвертация между Python и JSON', 'Кэширование', 'Маршрутизация', 'b'),
        ], 1):
            Question.objects.create(test=t3, question_type='quiz', text=q[0],
                option_a=q[1], option_b=q[2], option_c=q[3], option_d=q[4],
                correct_answer=q[5], order=i)

        # ===== JavaScript Basics =====
        t4 = SkillTest.objects.create(
            title='JavaScript: Основы', language='javascript', difficulty='easy',
            description='Типы данных, функции, DOM, события, основы ES6+.')
        for i, q in enumerate([
            ('Чем отличается let от var?', 'Ничем', 'let имеет блочную область видимости', 'var новее', 'let нельзя переприсвоить', 'b'),
            ('Что вернёт typeof null?', 'null', 'undefined', 'object', 'boolean', 'c'),
            ('Что такое промис (Promise)?', 'Тип данных', 'Объект для асинхронных операций', 'Метод массива', 'Оператор', 'b'),
            ('Как добавить элемент в конец массива?', 'arr.add()', 'arr.push()', 'arr.append()', 'arr.insert()', 'b'),
            ('Что делает === в JavaScript?', 'Присваивание', 'Сравнение с приведением типов', 'Строгое сравнение', 'Логическое И', 'c'),
            ('Что такое event.preventDefault()?', 'Удаляет событие', 'Отменяет действие по умолчанию', 'Создаёт событие', 'Останавливает всплытие', 'b'),
            ('Как объявить стрелочную функцию?', 'function => {}', 'const fn = () => {}', 'arrow fn() {}', 'def fn():', 'b'),
            ('Что такое localStorage?', 'Серверное хранилище', 'Хранилище в браузере', 'База данных', 'Cookie', 'b'),
        ], 1):
            Question.objects.create(test=t4, question_type='quiz', text=q[0],
                option_a=q[1], option_b=q[2], option_c=q[3], option_d=q[4],
                correct_answer=q[5], order=i)

        # ===== React =====
        t5 = SkillTest.objects.create(
            title='React Fundamentals', language='react', difficulty='medium',
            description='Компоненты, хуки, состояние, пропсы, жизненный цикл.')
        for i, q in enumerate([
            ('Что такое JSX?', 'Новый язык', 'Синтаксическое расширение JavaScript', 'Фреймворк', 'Библиотека стилей', 'b'),
            ('Какой хук используется для состояния?', 'useEffect', 'useState', 'useContext', 'useReducer', 'b'),
            ('Когда вызывается useEffect без зависимостей ([])?', 'Каждый рендер', 'Только при монтировании', 'При размонтировании', 'Никогда', 'b'),
            ('Что такое props?', 'Состояние компонента', 'Данные, переданные от родителя', 'Стили', 'События', 'b'),
            ('Как обновить состояние в React?', 'state = newValue', 'setState(newValue)', 'this.state = x', 'update(state)', 'b'),
            ('Что такое Virtual DOM?', 'Реальный DOM', 'Легковесная копия DOM в памяти', 'CSS-фреймворк', 'Node.js модуль', 'b'),
            ('Для чего нужен key в списках?', 'Для стилей', 'Для идентификации элементов при ре-рендере', 'Для SEO', 'Для доступности', 'b'),
            ('Что делает useContext?', 'Создаёт API', 'Позволяет получить данные контекста', 'Управляет роутингом', 'Кэширует данные', 'b'),
            ('Как передать данные от ребёнка к родителю?', 'props', 'Через callback-функцию в props', 'useParent', 'emit()', 'b'),
            ('Что такое React.memo?', 'Хук для мемоизации', 'HOC для предотвращения лишних рендеров', 'Хранилище', 'Роутер', 'b'),
        ], 1):
            Question.objects.create(test=t5, question_type='quiz', text=q[0],
                option_a=q[1], option_b=q[2], option_c=q[3], option_d=q[4],
                correct_answer=q[5], order=i)

        # ===== SQL =====
        t6 = SkillTest.objects.create(
            title='SQL и базы данных', language='general', difficulty='easy',
            description='SELECT, JOIN, агрегация, индексы, нормализация.')
        for i, q in enumerate([
            ('Какой оператор используется для выборки данных?', 'GET', 'FETCH', 'SELECT', 'FIND', 'c'),
            ('Что делает INNER JOIN?', 'Все записи из обеих таблиц', 'Только совпадающие записи', 'Только из левой', 'Только из правой', 'b'),
            ('Какая функция считает количество строк?', 'SUM()', 'COUNT()', 'TOTAL()', 'LEN()', 'b'),
            ('Что такое PRIMARY KEY?', 'Внешний ключ', 'Уникальный идентификатор строки', 'Индекс', 'Ограничение на NULL', 'b'),
            ('Как отсортировать по убыванию?', 'ORDER BY col ASC', 'ORDER BY col DESC', 'SORT BY col DOWN', 'GROUP BY col DESC', 'b'),
            ('Что такое индекс в БД?', 'Номер строки', 'Структура для ускорения поиска', 'Тип данных', 'Бэкап', 'b'),
            ('Что делает GROUP BY?', 'Сортирует', 'Группирует для агрегации', 'Фильтрует', 'Соединяет таблицы', 'b'),
            ('Какой оператор фильтрует агрегированные данные?', 'WHERE', 'HAVING', 'FILTER', 'WHEN', 'b'),
        ], 1):
            Question.objects.create(test=t6, question_type='quiz', text=q[0],
                option_a=q[1], option_b=q[2], option_c=q[3], option_d=q[4],
                correct_answer=q[5], order=i)

        # ===== Git =====
        t7 = SkillTest.objects.create(
            title='Git и системы контроля версий', language='general', difficulty='easy',
            description='Основы Git: коммиты, ветки, merge, pull request.')
        for i, q in enumerate([
            ('Какая команда создаёт новый репозиторий?', 'git start', 'git init', 'git create', 'git new', 'b'),
            ('Что делает git add?', 'Создаёт коммит', 'Добавляет файлы в staging', 'Пушит на сервер', 'Создаёт ветку', 'b'),
            ('Как создать новую ветку?', 'git branch name', 'git new branch', 'git create name', 'git fork name', 'a'),
            ('Что делает git pull?', 'Пушит изменения', 'Скачивает и мержит изменения', 'Создаёт PR', 'Удаляет ветку', 'b'),
            ('Что такое merge conflict?', 'Ошибка push', 'Конфликт при слиянии веток', 'Баг в коде', 'Проблема с сетью', 'b'),
            ('Какая команда показывает историю коммитов?', 'git history', 'git log', 'git show', 'git list', 'b'),
            ('Что делает .gitignore?', 'Удаляет файлы', 'Указывает файлы, которые Git игнорирует', 'Создаёт бэкап', 'Настраивает Git', 'b'),
            ('Как отменить последний коммит (сохранив изменения)?', 'git undo', 'git reset --soft HEAD~1', 'git revert HEAD', 'git delete last', 'b'),
        ], 1):
            Question.objects.create(test=t7, question_type='quiz', text=q[0],
                option_a=q[1], option_b=q[2], option_c=q[3], option_d=q[4],
                correct_answer=q[5], order=i)

        # ===== Java =====
        t8 = SkillTest.objects.create(
            title='Java: Основы', language='java', difficulty='easy',
            description='ООП, типы данных, коллекции, исключения в Java.')
        for i, q in enumerate([
            ('Какой тип является ссылочным?', 'int', 'double', 'String', 'boolean', 'c'),
            ('Что такое наследование?', 'Копирование кода', 'Создание класса на основе другого', 'Шаблон проектирования', 'Тип данных', 'b'),
            ('Какое ключевое слово запрещает наследование?', 'static', 'abstract', 'final', 'private', 'c'),
            ('Что такое interface в Java?', 'Визуальный компонент', 'Контракт, описывающий методы', 'Тип переменной', 'Библиотека', 'b'),
            ('Как обработать исключение?', 'try/catch', 'handle/error', 'begin/rescue', 'error/resolve', 'a'),
            ('Что такое ArrayList?', 'Статический массив', 'Динамическая коллекция', 'Связный список', 'Карта', 'b'),
            ('Какой модификатор ограничивает доступ только классом?', 'public', 'protected', 'private', 'default', 'c'),
            ('Что делает ключевое слово static?', 'Создаёт объект', 'Принадлежит классу, а не объекту', 'Делает переменную константой', 'Наследует метод', 'b'),
        ], 1):
            Question.objects.create(test=t8, question_type='quiz', text=q[0],
                option_a=q[1], option_b=q[2], option_c=q[3], option_d=q[4],
                correct_answer=q[5], order=i)

        # ===== Docker & DevOps =====
        t9 = SkillTest.objects.create(
            title='Docker и DevOps', language='general', difficulty='medium',
            description='Контейнеры, образы, Docker Compose, CI/CD, базовый Kubernetes.')
        for i, q in enumerate([
            ('Что такое Docker-контейнер?', 'Виртуальная машина', 'Изолированный процесс с приложением', 'Операционная система', 'Сервер', 'b'),
            ('Что описывает Dockerfile?', 'Конфигурацию сервера', 'Инструкции для сборки образа', 'Настройки сети', 'Логи приложения', 'b'),
            ('Что делает docker-compose up?', 'Скачивает Docker', 'Запускает мультиконтейнерное приложение', 'Обновляет образ', 'Удаляет контейнеры', 'b'),
            ('Что такое CI/CD?', 'Язык программирования', 'Непрерывная интеграция и доставка', 'Система мониторинга', 'База данных', 'b'),
            ('Какая команда показывает запущенные контейнеры?', 'docker list', 'docker ps', 'docker show', 'docker running', 'b'),
            ('Что такое Docker volume?', 'Сеть', 'Постоянное хранилище данных', 'Образ', 'Лог', 'b'),
            ('Что такое Kubernetes Pod?', 'Кластер', 'Минимальная единица развёртывания', 'Сервис', 'Namespace', 'b'),
            ('Для чего нужен .dockerignore?', 'Настройка сети', 'Исключение файлов из контекста сборки', 'Логирование', 'Безопасность', 'b'),
        ], 1):
            Question.objects.create(test=t9, question_type='quiz', text=q[0],
                option_a=q[1], option_b=q[2], option_c=q[3], option_d=q[4],
                correct_answer=q[5], order=i)

        # ===== JavaScript Advanced =====
        t10 = SkillTest.objects.create(
            title='JavaScript: Продвинутый', language='javascript', difficulty='hard',
            description='Замыкания, прототипы, async/await, Event Loop, паттерны.')
        for i, q in enumerate([
            ('Что такое замыкание (closure)?', 'Цикл', 'Функция с доступом к переменным внешней области', 'Объект', 'Массив', 'b'),
            ('Что вернёт Promise.all при reject одного промиса?', 'Все результаты', 'Reject целиком', 'Только resolve', 'Undefined', 'b'),
            ('Что такое Event Loop?', 'Цикл for', 'Механизм обработки асинхронных задач', 'Событие DOM', 'Метод массива', 'b'),
            ('Чем отличается setTimeout от setInterval?', 'Ничем', 'setTimeout — один раз, setInterval — повторяется', 'setInterval быстрее', 'setTimeout для DOM', 'b'),
            ('Что такое прототип в JavaScript?', 'Шаблон класса', 'Объект, от которого наследуются свойства', 'Тип данных', 'Функция', 'b'),
            ('Что делает Object.freeze()?', 'Удаляет объект', 'Запрещает изменение объекта', 'Копирует объект', 'Сериализует', 'b'),
            ('Что такое WeakMap?', 'Обычная Map', 'Map с слабыми ссылками на ключи', 'Иммутабельная Map', 'Массив', 'b'),
            ('Для чего используется Symbol?', 'Для строк', 'Для создания уникальных идентификаторов', 'Для чисел', 'Для массивов', 'b'),
            ('Что такое debounce?', 'Оптимизация рендера', 'Задержка вызова функции до прекращения событий', 'Тип промиса', 'Метод массива', 'b'),
            ('Что делает async/await?', 'Создаёт потоки', 'Упрощает работу с промисами', 'Ускоряет код', 'Блокирует Event Loop', 'b'),
        ], 1):
            Question.objects.create(test=t10, question_type='quiz', text=q[0],
                option_a=q[1], option_b=q[2], option_c=q[3], option_d=q[4],
                correct_answer=q[5], order=i)

        # ===== Code Challenges =====
        code_test = SkillTest.objects.create(
            title='Python: Live Coding', language='python', difficulty='hard',
            description='Практические задачи на алгоритмы и структуры данных. Напишите код и проверьте его тестами.')

        Question.objects.create(
            test=code_test, question_type='code', order=1,
            text='Реализуйте функцию flatten(lst), которая принимает вложенный список произвольной глубины и возвращает плоский список всех элементов.\n\nПример: flatten([1, [2, [3, 4], 5], 6]) → [1, 2, 3, 4, 5, 6]',
            code_template='def flatten(lst):\n    # Ваш код здесь\n    pass',
            test_code="""def _t1():
    _check(flatten([1, 2, 3]) == [1, 2, 3], f"Ожидалось [1,2,3], получено {flatten([1,2,3])}")
_run_test('Плоский список без вложенности', _t1)

def _t2():
    _check(flatten([1, [2, 3], 4]) == [1, 2, 3, 4], f"Ожидалось [1,2,3,4], получено {flatten([1,[2,3],4])}")
_run_test('Один уровень вложенности', _t2)

def _t3():
    _check(flatten([1, [2, [3, [4, [5]]]]]) == [1, 2, 3, 4, 5], f"Получено {flatten([1,[2,[3,[4,[5]]]]])}")
_run_test('Глубокая вложенность', _t3)

def _t4():
    _check(flatten([]) == [], f"Ожидалось [], получено {flatten([])}")
_run_test('Пустой список', _t4)

def _t5():
    _check(flatten([[1, 2], [], [3, [4, 5]], 6]) == [1, 2, 3, 4, 5, 6])
_run_test('Смешанные типы и пустые подсписки', _t5)""",
        )

        Question.objects.create(
            test=code_test, question_type='code', order=2,
            text='Реализуйте функцию group_by(items, key_func), которая группирует элементы списка по результату key_func. Возвращает словарь {ключ: [элементы]}.\n\nПример: group_by([1,2,3,4,5,6], lambda x: x % 2) → {1: [1,3,5], 0: [2,4,6]}',
            code_template='def group_by(items, key_func):\n    # Ваш код здесь\n    pass',
            test_code="""def _t1():
    result = group_by([1,2,3,4,5,6], lambda x: x % 2)
    _check(result == {1: [1,3,5], 0: [2,4,6]}, f"Получено {result}")
_run_test('Группировка по чётности', _t1)

def _t2():
    result = group_by(['hi', 'hey', 'ok', 'bye'], lambda s: len(s))
    _check(result == {2: ['hi', 'ok'], 3: ['hey', 'bye']}, f"Получено {result}")
_run_test('Группировка строк по длине', _t2)

def _t3():
    _check(group_by([], lambda x: x) == {}, "Пустой список должен вернуть {}")
_run_test('Пустой список', _t3)

def _t4():
    result = group_by([1,2,3], lambda x: x)
    _check(result == {1: [1], 2: [2], 3: [3]}, f"Получено {result}")
_run_test('Один элемент в каждой группе', _t4)""",
        )

        Question.objects.create(
            test=code_test, question_type='code', order=3,
            text='Реализуйте функцию memoize(func), которая возвращает обёрнутую функцию с кэшированием результатов. При повторном вызове с теми же аргументами должна возвращать закэшированный результат.\n\nПример:\n@memoize\ndef add(a, b): return a + b\nadd(1, 2)  # вычисляет\nadd(1, 2)  # из кэша',
            code_template='def memoize(func):\n    # Ваш код здесь\n    pass',
            test_code="""def _test_basic_memoize():
    call_count = [0]
    @memoize
    def add(a, b):
        call_count[0] += 1
        return a + b
    _check(add(1, 2) == 3, f"add(1,2) вернул {add(1,2)}")
    _check(add(1, 2) == 3, "Повторный вызов должен вернуть то же")
    _check(call_count[0] == 1, f"Функция вызвана {call_count[0]} раз, ожидалось 1")

_run_test('Кэширование повторных вызовов', _test_basic_memoize)

def _test_different_args():
    call_count = [0]
    @memoize
    def mul(a, b):
        call_count[0] += 1
        return a * b
    _check(mul(2, 3) == 6, f"mul(2,3) = {mul(2,3)}")
    _check(mul(3, 4) == 12, f"mul(3,4) = {mul(3,4)}")
    _check(mul(2, 3) == 6, "Кэш не сработал")
    _check(call_count[0] == 2, f"Вызовов: {call_count[0]}, ожидалось 2")

_run_test('Разные аргументы — разные вызовы', _test_different_args)

def _test_no_args():
    call_count = [0]
    @memoize
    def greet():
        call_count[0] += 1
        return 'hello'
    _check(greet() == 'hello', f"Получено {greet()}")
    _check(greet() == 'hello', "Повтор не из кэша")
    _check(call_count[0] == 1, f"Вызовов: {call_count[0]}, ожидалось 1")

_run_test('Функция без аргументов', _test_no_args)""",
        )

        Question.objects.create(
            test=code_test, question_type='code', order=4,
            text='Реализуйте функцию find_pairs(nums, target), которая находит все уникальные пары чисел в списке, сумма которых равна target. Каждая пара — кортеж (a, b) где a <= b. Пары не должны повторяться.\n\nПример: find_pairs([1,2,3,4,5], 6) → [(1,5), (2,4)]',
            code_template='def find_pairs(nums, target):\n    # Ваш код здесь\n    pass',
            test_code="""def _t1():
    result = sorted(find_pairs([1,2,3,4,5], 6))
    _check(result == [(1,5), (2,4)], f"Получено {result}")
_run_test('Базовый случай', _t1)

def _t2():
    result = sorted(find_pairs([1,1,2,3,3,4,5], 4))
    _check(result == [(1,3)], f"Дубли не убраны: {result}")
_run_test('Дубликаты в списке', _t2)

def _t3():
    _check(find_pairs([1,2,3], 10) == [], "Должен вернуть []")
_run_test('Нет пар', _t3)

def _t4():
    result = sorted(find_pairs([-2,-1,0,1,2,3], 1))
    _check(result == [(-2,3), (-1,2), (0,1)], f"Получено {result}")
_run_test('Отрицательные числа', _t4)

def _t5():
    _check(find_pairs([], 5) == [], "Пустой список → []")
_run_test('Пустой список', _t5)""",
        )

        Question.objects.create(
            test=code_test, question_type='code', order=5,
            text='Реализуйте класс LRUCache(capacity), который поддерживает операции get(key) и put(key, value) за O(1). При превышении capacity удаляется наименее используемый элемент.\n\nПример:\ncache = LRUCache(2)\ncache.put(1, 1)\ncache.put(2, 2)\ncache.get(1)    → 1\ncache.put(3, 3) # удаляет key=2\ncache.get(2)    → -1',
            code_template='class LRUCache:\n    def __init__(self, capacity):\n        # Ваш код здесь\n        pass\n\n    def get(self, key):\n        # Ваш код здесь\n        pass\n\n    def put(self, key, value):\n        # Ваш код здесь\n        pass',
            test_code="""def _test_basic_lru():
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    _check(cache.get(1) == 1, f"get(1) = {cache.get(1)}, ожидалось 1")
    cache.put(3, 3)
    _check(cache.get(2) == -1, f"get(2) = {cache.get(2)}, ожидалось -1 (вытеснен)")

_run_test('Базовая LRU-логика', _test_basic_lru)

def _test_update_value():
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(1, 10)
    _check(cache.get(1) == 10, f"get(1) = {cache.get(1)}, ожидалось 10")

_run_test('Обновление значения по ключу', _test_update_value)

def _test_capacity_one():
    cache = LRUCache(1)
    cache.put(1, 1)
    cache.put(2, 2)
    _check(cache.get(1) == -1, f"get(1) = {cache.get(1)}, должен быть вытеснен")
    _check(cache.get(2) == 2, f"get(2) = {cache.get(2)}, ожидалось 2")

_run_test('Capacity = 1', _test_capacity_one)

def _test_access_refreshes():
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.get(1)
    cache.put(3, 3)
    _check(cache.get(1) == 1, f"get(1) = {cache.get(1)}, доступ должен обновить приоритет")
    _check(cache.get(2) == -1, f"get(2) = {cache.get(2)}, должен быть вытеснен")

_run_test('Доступ обновляет приоритет', _test_access_refreshes)""",
        )

        # ===== Python: Структуры данных и алгоритмы =====
        code_test2 = SkillTest.objects.create(
            title='Python: Алгоритмы', language='python', difficulty='hard',
            description='Алгоритмические задачи: деревья, графы, динамическое программирование, обработка строк.')

        Question.objects.create(
            test=code_test2, question_type='code', order=1,
            text='Реализуйте функцию is_valid_brackets(s), которая проверяет корректность скобочной последовательности. Строка содержит только символы ()[]{}.\n\nПример: is_valid_brackets("({[]})") → True\nis_valid_brackets("([)]") → False',
            code_template='def is_valid_brackets(s):\n    # Ваш код здесь\n    pass',
            test_code="""def _t1():
    _check(is_valid_brackets("()") == True, "() должно быть True")
_run_test('Простые круглые скобки', _t1)

def _t2():
    _check(is_valid_brackets("({[]})") == True, "({[]}) должно быть True")
_run_test('Вложенные разные скобки', _t2)

def _t3():
    _check(is_valid_brackets("([)]") == False, "([)] должно быть False")
_run_test('Неправильное пересечение', _t3)

def _t4():
    _check(is_valid_brackets("") == True, "Пустая строка - True")
_run_test('Пустая строка', _t4)

def _t5():
    _check(is_valid_brackets("{[()]}(){}") == True)
_run_test('Длинная корректная последовательность', _t5)

def _t6():
    _check(is_valid_brackets("((((") == False, "Незакрытые скобки")
_run_test('Незакрытые скобки', _t6)""",
        )

        Question.objects.create(
            test=code_test2, question_type='code', order=2,
            text='Реализуйте функцию longest_unique_substring(s), которая возвращает длину самой длинной подстроки без повторяющихся символов.\n\nПример: longest_unique_substring("abcabcbb") → 3 ("abc")\nlongest_unique_substring("bbbbb") → 1',
            code_template='def longest_unique_substring(s):\n    # Ваш код здесь\n    pass',
            test_code="""def _t1():
    _check(longest_unique_substring("abcabcbb") == 3, f"Получено {longest_unique_substring('abcabcbb')}")
_run_test('abcabcbb → 3', _t1)

def _t2():
    _check(longest_unique_substring("bbbbb") == 1, f"Получено {longest_unique_substring('bbbbb')}")
_run_test('bbbbb → 1', _t2)

def _t3():
    _check(longest_unique_substring("pwwkew") == 3, f"Получено {longest_unique_substring('pwwkew')}")
_run_test('pwwkew → 3', _t3)

def _t4():
    _check(longest_unique_substring("") == 0)
_run_test('Пустая строка → 0', _t4)

def _t5():
    _check(longest_unique_substring("abcdef") == 6)
_run_test('Все уникальные → длина строки', _t5)""",
        )

        Question.objects.create(
            test=code_test2, question_type='code', order=3,
            text='Реализуйте функцию merge_intervals(intervals), которая сливает пересекающиеся интервалы. Каждый интервал — кортеж (start, end).\n\nПример: merge_intervals([(1,3),(2,6),(8,10),(15,18)]) → [(1,6),(8,10),(15,18)]',
            code_template='def merge_intervals(intervals):\n    # Ваш код здесь\n    pass',
            test_code="""def _t1():
    result = merge_intervals([(1,3),(2,6),(8,10),(15,18)])
    _check(result == [(1,6),(8,10),(15,18)], f"Получено {result}")
_run_test('Стандартный случай', _t1)

def _t2():
    result = merge_intervals([(1,4),(4,5)])
    _check(result == [(1,5)], f"Получено {result}")
_run_test('Граничное касание', _t2)

def _t3():
    _check(merge_intervals([]) == [], "Пустой → []")
_run_test('Пустой список', _t3)

def _t4():
    result = merge_intervals([(1,10),(2,3),(4,5),(6,7)])
    _check(result == [(1,10)], f"Получено {result}")
_run_test('Один большой покрывает все', _t4)

def _t5():
    result = merge_intervals([(1,2),(3,4),(5,6)])
    _check(result == [(1,2),(3,4),(5,6)], f"Получено {result}")
_run_test('Нет пересечений', _t5)""",
        )

        Question.objects.create(
            test=code_test2, question_type='code', order=4,
            text='Реализуйте функцию max_profit(prices), которая возвращает максимальную прибыль от одной покупки и продажи акции. prices[i] — цена в день i. Нельзя продать до покупки.\n\nПример: max_profit([7,1,5,3,6,4]) → 5 (купить за 1, продать за 6)',
            code_template='def max_profit(prices):\n    # Ваш код здесь\n    pass',
            test_code="""def _t1():
    _check(max_profit([7,1,5,3,6,4]) == 5, f"Получено {max_profit([7,1,5,3,6,4])}")
_run_test('Стандартный случай → 5', _t1)

def _t2():
    _check(max_profit([7,6,4,3,1]) == 0, f"Получено {max_profit([7,6,4,3,1])}")
_run_test('Убывающие цены → 0', _t2)

def _t3():
    _check(max_profit([1,2]) == 1)
_run_test('Два элемента', _t3)

def _t4():
    _check(max_profit([2,4,1,7]) == 6, f"Получено {max_profit([2,4,1,7])}")
_run_test('Минимум в середине', _t4)

def _t5():
    _check(max_profit([]) == 0)
_run_test('Пустой список', _t5)""",
        )

        Question.objects.create(
            test=code_test2, question_type='code', order=5,
            text='Реализуйте функцию spiral_order(matrix), которая возвращает элементы матрицы в порядке спирали (по часовой стрелке, начиная с верхнего левого угла).\n\nПример: spiral_order([[1,2,3],[4,5,6],[7,8,9]]) → [1,2,3,6,9,8,7,4,5]',
            code_template='def spiral_order(matrix):\n    # Ваш код здесь\n    pass',
            test_code="""def _t1():
    result = spiral_order([[1,2,3],[4,5,6],[7,8,9]])
    _check(result == [1,2,3,6,9,8,7,4,5], f"Получено {result}")
_run_test('Матрица 3x3', _t1)

def _t2():
    result = spiral_order([[1,2,3,4],[5,6,7,8],[9,10,11,12]])
    _check(result == [1,2,3,4,8,12,11,10,9,5,6,7], f"Получено {result}")
_run_test('Матрица 3x4', _t2)

def _t3():
    _check(spiral_order([[1]]) == [1])
_run_test('Матрица 1x1', _t3)

def _t4():
    _check(spiral_order([]) == [])
_run_test('Пустая матрица', _t4)

def _t5():
    result = spiral_order([[1,2],[3,4]])
    _check(result == [1,2,4,3], f"Получено {result}")
_run_test('Матрица 2x2', _t5)""",
        )

        # ===== JavaScript: Live Coding =====
        code_test_js = SkillTest.objects.create(
            title='JavaScript: Live Coding', language='javascript', difficulty='hard',
            description='Практические задачи на JavaScript: замыкания, промисы, прототипы, работа с массивами и объектами.')

        Question.objects.create(
            test=code_test_js, question_type='code', order=1,
            text='Реализуйте функцию debounce(fn, delay), которая возвращает функцию, откладывающую вызов fn на delay мс. Повторный вызов сбрасывает таймер.\n\nПример:\nconst log = debounce(console.log, 100)\nlog("a") // отменено\nlog("b") // выполнится через 100мс',
            code_template='def debounce(fn, delay):\n    # Эмуляция debounce на Python\n    # (для демонстрации логики)\n    pass',
            test_code="""import time

def _t1():
    calls = []
    def fn(x):
        calls.append(x)
    debounced = debounce(fn, 0.05)
    debounced("a")
    debounced("b")
    debounced("c")
    time.sleep(0.1)
    _check(calls == ["c"], f"Должен быть только последний вызов, получено {calls}")
_run_test('Только последний вызов выполняется', _t1)

def _t2():
    calls = []
    def fn(x):
        calls.append(x)
    debounced = debounce(fn, 0.05)
    debounced("a")
    time.sleep(0.1)
    debounced("b")
    time.sleep(0.1)
    _check(calls == ["a", "b"], f"Оба вызова с паузой, получено {calls}")
_run_test('Вызовы с достаточной паузой', _t2)

def _t3():
    calls = []
    def fn():
        calls.append(1)
    debounced = debounce(fn, 0.05)
    debounced()
    time.sleep(0.1)
    _check(len(calls) == 1, f"Один вызов, получено {len(calls)}")
_run_test('Функция без аргументов', _t3)""",
        )

        Question.objects.create(
            test=code_test_js, question_type='code', order=2,
            text='Реализуйте функцию deep_equal(a, b), которая рекурсивно сравнивает два объекта (dict/list/примитивы). Возвращает True если структуры идентичны.\n\nПример: deep_equal({"a": [1,2]}, {"a": [1,2]}) → True\ndeep_equal({"a": 1}, {"a": 2}) → False',
            code_template='def deep_equal(a, b):\n    # Ваш код здесь\n    pass',
            test_code="""def _t1():
    _check(deep_equal({"a": 1, "b": 2}, {"a": 1, "b": 2}) == True)
_run_test('Одинаковые словари', _t1)

def _t2():
    _check(deep_equal({"a": [1, {"b": 2}]}, {"a": [1, {"b": 2}]}) == True)
_run_test('Глубокая вложенность', _t2)

def _t3():
    _check(deep_equal({"a": 1}, {"a": 2}) == False)
_run_test('Разные значения', _t3)

def _t4():
    _check(deep_equal([1, [2, [3]]], [1, [2, [3]]]) == True)
_run_test('Вложенные списки', _t4)

def _t5():
    _check(deep_equal({"a": 1}, {"a": 1, "b": 2}) == False)
_run_test('Разное количество ключей', _t5)

def _t6():
    _check(deep_equal(None, None) == True)
    _check(deep_equal(0, False) == False)
_run_test('None и примитивы', _t6)""",
        )

        Question.objects.create(
            test=code_test_js, question_type='code', order=3,
            text='Реализуйте функцию pipe(*functions), которая возвращает функцию-конвейер: результат каждой функции передаётся как аргумент следующей.\n\nПример:\nadd1 = lambda x: x + 1\nmul2 = lambda x: x * 2\nf = pipe(add1, mul2, add1)\nf(5) → 13  # (5+1)*2+1',
            code_template='def pipe(*functions):\n    # Ваш код здесь\n    pass',
            test_code="""def _t1():
    add1 = lambda x: x + 1
    mul2 = lambda x: x * 2
    f = pipe(add1, mul2)
    _check(f(5) == 12, f"pipe(add1, mul2)(5) = {f(5)}, ожидалось 12")
_run_test('Две функции', _t1)

def _t2():
    add1 = lambda x: x + 1
    mul2 = lambda x: x * 2
    sub3 = lambda x: x - 3
    f = pipe(add1, mul2, sub3)
    _check(f(5) == 9, f"Получено {f(5)}")
_run_test('Три функции', _t2)

def _t3():
    f = pipe()
    _check(f(42) == 42, "Пустой pipe возвращает значение как есть")
_run_test('Пустой pipe', _t3)

def _t4():
    upper = lambda s: s.upper()
    excl = lambda s: s + "!"
    f = pipe(upper, excl)
    _check(f("hello") == "HELLO!", f"Получено {f('hello')}")
_run_test('Работа со строками', _t4)""",
        )

        Question.objects.create(
            test=code_test_js, question_type='code', order=4,
            text='Реализуйте функцию throttle(fn, interval), которая ограничивает частоту вызовов fn. Первый вызов выполняется сразу, последующие — не чаще чем раз в interval секунд.\n\nПример: throttled = throttle(print, 0.1)\nthrottled("a")  # выполнится сразу\nthrottled("b")  # игнорируется (слишком рано)',
            code_template='def throttle(fn, interval):\n    # Ваш код здесь\n    pass',
            test_code="""import time

def _t1():
    calls = []
    def fn(x):
        calls.append(x)
    throttled = throttle(fn, 0.1)
    throttled("a")
    _check(calls == ["a"], f"Первый вызов сразу, получено {calls}")
_run_test('Первый вызов выполняется сразу', _t1)

def _t2():
    calls = []
    def fn(x):
        calls.append(x)
    throttled = throttle(fn, 0.1)
    throttled("a")
    throttled("b")
    throttled("c")
    _check(calls == ["a"], f"Повторные игнорируются, получено {calls}")
_run_test('Повторные вызовы игнорируются', _t2)

def _t3():
    calls = []
    def fn(x):
        calls.append(x)
    throttled = throttle(fn, 0.05)
    throttled("a")
    time.sleep(0.08)
    throttled("b")
    _check(calls == ["a", "b"], f"После паузы можно вызвать, получено {calls}")
_run_test('После interval можно вызвать снова', _t3)""",
        )

        Question.objects.create(
            test=code_test_js, question_type='code', order=5,
            text='Реализуйте функцию retry(fn, max_attempts, delay), которая вызывает fn() и при исключении повторяет попытку до max_attempts раз с задержкой delay секунд. Возвращает результат при успехе или выбрасывает последнее исключение.\n\nПример: retry(unstable_api_call, 3, 0.1)',
            code_template='def retry(fn, max_attempts, delay=0):\n    # Ваш код здесь\n    pass',
            test_code="""import time

def _t1():
    result = retry(lambda: 42, 3)
    _check(result == 42, f"Получено {result}")
_run_test('Успешный первый вызов', _t1)

def _t2():
    counter = [0]
    def flaky():
        counter[0] += 1
        if counter[0] < 3:
            raise ValueError("fail")
        return "ok"
    result = retry(flaky, 5, 0)
    _check(result == "ok", f"Получено {result}")
    _check(counter[0] == 3, f"Вызовов: {counter[0]}, ожидалось 3")
_run_test('Успех на третью попытку', _t2)

def _t3():
    def always_fail():
        raise RuntimeError("error")
    try:
        retry(always_fail, 3, 0)
        _check(False, "Должно было выбросить исключение")
    except RuntimeError as e:
        _check(str(e) == "error")
_run_test('Все попытки неудачны — выбрасывает исключение', _t3)

def _t4():
    counter = [0]
    def fn():
        counter[0] += 1
        raise Exception("x")
    try:
        retry(fn, 4, 0)
    except:
        pass
    _check(counter[0] == 4, f"Должно быть 4 попытки, получено {counter[0]}")
_run_test('Количество попыток = max_attempts', _t4)""",
        )

        # ===== Python: Функциональное программирование =====
        code_test3 = SkillTest.objects.create(
            title='Python: Функциональные паттерны', language='python', difficulty='medium',
            description='Функциональный стиль: map/filter/reduce, каррирование, генераторы, итераторы.')

        Question.objects.create(
            test=code_test3, question_type='code', order=1,
            text='Реализуйте функцию compose(*fns), которая принимает функции и возвращает их композицию (справа налево). compose(f, g, h)(x) == f(g(h(x)))\n\nПример:\ndouble = lambda x: x * 2\ninc = lambda x: x + 1\ncompose(double, inc)(3) → 8  # double(inc(3))',
            code_template='def compose(*fns):\n    # Ваш код здесь\n    pass',
            test_code="""def _t1():
    double = lambda x: x * 2
    inc = lambda x: x + 1
    f = compose(double, inc)
    _check(f(3) == 8, f"compose(double, inc)(3) = {f(3)}, ожидалось 8")
_run_test('double(inc(3)) = 8', _t1)

def _t2():
    f = compose(str, lambda x: x + 1, lambda x: x * 2)
    _check(f(3) == "7", f"Получено {f(3)}")
_run_test('Три функции: str(add1(mul2(3)))', _t2)

def _t3():
    f = compose()
    _check(f(5) == 5, "Пустой compose возвращает аргумент")
_run_test('Пустой compose', _t3)

def _t4():
    f = compose(lambda x: x.upper())
    _check(f("hello") == "HELLO")
_run_test('Одна функция', _t4)""",
        )

        Question.objects.create(
            test=code_test3, question_type='code', order=2,
            text='Реализуйте функцию curry(fn), которая возвращает каррированную версию функции. Каррированная функция принимает аргументы по одному.\n\nПример:\n@curry\ndef add(a, b, c): return a + b + c\nadd(1)(2)(3) → 6\nadd(1, 2)(3) → 6',
            code_template='def curry(fn):\n    # Ваш код здесь\n    pass',
            test_code="""def _t1():
    @curry
    def add(a, b):
        return a + b
    _check(add(1)(2) == 3, f"add(1)(2) = {add(1)(2)}")
_run_test('Два аргумента по одному', _t1)

def _t2():
    @curry
    def add3(a, b, c):
        return a + b + c
    _check(add3(1)(2)(3) == 6)
_run_test('Три аргумента по одному', _t2)

def _t3():
    @curry
    def add3(a, b, c):
        return a + b + c
    _check(add3(1, 2)(3) == 6, "Частичное применение")
_run_test('Частичное применение (2+1)', _t3)

def _t4():
    @curry
    def add(a, b):
        return a + b
    _check(add(1, 2) == 3, "Все аргументы сразу")
_run_test('Все аргументы сразу', _t4)""",
        )

        Question.objects.create(
            test=code_test3, question_type='code', order=3,
            text='Реализуйте генератор fibonacci(), который бесконечно генерирует числа Фибоначчи: 0, 1, 1, 2, 3, 5, 8, 13...\n\nПример:\nfib = fibonacci()\nnext(fib) → 0\nnext(fib) → 1\nnext(fib) → 1\nnext(fib) → 2',
            code_template='def fibonacci():\n    # Ваш код здесь\n    pass',
            test_code="""def _t1():
    fib = fibonacci()
    first_10 = [next(fib) for _ in range(10)]
    expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    _check(first_10 == expected, f"Первые 10: {first_10}")
_run_test('Первые 10 чисел Фибоначчи', _t1)

def _t2():
    fib = fibonacci()
    _check(next(fib) == 0, "Первый = 0")
    _check(next(fib) == 1, "Второй = 1")
_run_test('Начальные значения 0 и 1', _t2)

def _t3():
    fib = fibonacci()
    for _ in range(20):
        next(fib)
    val = next(fib)
    _check(val == 6765, f"fib(20) должно быть 6765, получено {val}")
_run_test('fib(20) = 6765', _t3)""",
        )

        Question.objects.create(
            test=code_test3, question_type='code', order=4,
            text='Реализуйте функцию chunk(lst, size), которая разбивает список на подсписки длиной size. Последний подсписок может быть короче.\n\nПример: chunk([1,2,3,4,5], 2) → [[1,2],[3,4],[5]]',
            code_template='def chunk(lst, size):\n    # Ваш код здесь\n    pass',
            test_code="""def _t1():
    result = chunk([1,2,3,4,5], 2)
    _check(result == [[1,2],[3,4],[5]], f"Получено {result}")
_run_test('Нечётное разбиение', _t1)

def _t2():
    result = chunk([1,2,3,4], 2)
    _check(result == [[1,2],[3,4]], f"Получено {result}")
_run_test('Ровное разбиение', _t2)

def _t3():
    _check(chunk([], 3) == [], "Пустой список → []")
_run_test('Пустой список', _t3)

def _t4():
    result = chunk([1,2,3], 5)
    _check(result == [[1,2,3]], f"Получено {result}")
_run_test('Size больше длины списка', _t4)

def _t5():
    result = chunk([1,2,3,4,5,6], 1)
    _check(result == [[1],[2],[3],[4],[5],[6]], f"Получено {result}")
_run_test('Size = 1', _t5)""",
        )

        Question.objects.create(
            test=code_test3, question_type='code', order=5,
            text='Реализуйте функцию once(fn), которая позволяет вызвать fn только один раз. Повторные вызовы возвращают результат первого вызова.\n\nПример:\ncounter = once(lambda: 42)\ncounter() → 42\ncounter() → 42 (fn не вызывается повторно)',
            code_template='def once(fn):\n    # Ваш код здесь\n    pass',
            test_code="""def _t1():
    calls = [0]
    def expensive():
        calls[0] += 1
        return "result"
    f = once(expensive)
    _check(f() == "result")
    _check(f() == "result")
    _check(calls[0] == 1, f"Вызовов: {calls[0]}, ожидалось 1")
_run_test('Функция вызывается только раз', _t1)

def _t2():
    f = once(lambda: 100)
    r1 = f()
    r2 = f()
    r3 = f()
    _check(r1 == r2 == r3 == 100)
_run_test('Все вызовы возвращают первый результат', _t2)

def _t3():
    calls = [0]
    def fn(x, y):
        calls[0] += 1
        return x + y
    f = once(fn)
    _check(f(1, 2) == 3)
    _check(f(10, 20) == 3, "Повторный вызов с другими args -> первый результат")
    _check(calls[0] == 1)
_run_test('Аргументы второго вызова игнорируются', _t3)""",
        )

        self.stdout.write(f'    Tests: {SkillTest.objects.count()}, Questions: {Question.objects.count()}')

    def _create_applications(self):
        self.stdout.write('  Creating applications...')
        if Application.objects.exists():
            self.stdout.write('    Applications already exist, skipping.')
            return

        alice = User.objects.get(username='alice')
        bob = User.objects.get(username='bob')
        charlie = User.objects.get(username='charlie')
        diana = User.objects.get(username='diana')
        fatima = User.objects.get(username='fatima')
        julia = User.objects.get(username='julia')
        hana = User.objects.get(username='hana')
        marat = User.objects.get(username='marat')
        nastya = User.objects.get(username='nastya')
        ivan = User.objects.get(username='ivan')
        erik = User.objects.get(username='erik')

        jobs = {j.title + '|' + j.company: j for j in Job.objects.all()}

        def get_job(title, company='TechCorp Kazakhstan'):
            return jobs.get(f'{title}|{company}')

        apps = [
            # === Отклики на TechCorp (основная компания — много откликов) ===
            (alice, 'Junior Python Developer', 'TechCorp Kazakhstan',
             'Привет! Я изучаю Python уже полгода, написала несколько pet-проектов на Django. Очень хочу попасть к вам в команду!', 'pending'),
            (marat, 'Junior Python Developer', 'TechCorp Kazakhstan',
             'Студент 3 курса, учу Python. Хочу стажировку или junior-позицию. Готов учиться!', 'pending'),
            (hana, 'Junior Python Developer', 'TechCorp Kazakhstan',
             'Перехожу из QA в разработку. Знаю Python, Selenium, SQL. Хочу расти как разработчик.', 'reviewed'),
            (charlie, 'Junior Python Developer', 'TechCorp Kazakhstan',
             'У меня 2 года опыта, но готов рассмотреть и junior-позицию в вашей компании.', 'reviewed'),

            (bob, 'Junior Frontend Developer (React)', 'TechCorp Kazakhstan',
             'React — моя главная технология. Сделал SPA для управления задачами. Портфолио на GitHub.', 'accepted'),
            (julia, 'Junior Frontend Developer (React)', 'TechCorp Kazakhstan',
             'Выпускница bootcamp, сделала 5 проектов на React! Готова к работе.', 'pending'),
            (nastya, 'Junior Frontend Developer (React)', 'TechCorp Kazakhstan',
             '2 года во frontend, знаю React и Vue. Хочу в продуктовую компанию.', 'reviewed'),

            (charlie, 'Middle Python Developer', 'TechCorp Kazakhstan',
             'Два года опыта Python + Django в продакшне. Работал с Celery и Redis. Готов к highload.', 'accepted'),
            (erik, 'Senior Backend Developer (Python)', 'TechCorp Kazakhstan',
             '10 лет опыта в backend. Лидировал команды, проектировал микросервисы. Готов к новым вызовам.', 'pending'),

            (diana, 'Junior Java Developer', 'TechCorp Kazakhstan',
             'Закончила курсы Java, написала проект на Spring Boot. Хочу расти в банковской разработке!', 'pending'),
            (hana, 'Junior QA Engineer', 'TechCorp Kazakhstan',
             'Опыт ручного тестирования 8 месяцев. Начинаю автоматизацию на Python + Selenium.', 'accepted'),

            (nastya, 'Middle Frontend Developer (React)', 'TechCorp Kazakhstan',
             'React — основной фреймворк 2 года. TypeScript, Redux. Хочу в финтех.', 'pending'),
            (bob, 'Middle Frontend Developer (React)', 'TechCorp Kazakhstan',
             'Растущий frontend-разработчик, хочу вырасти до middle.', 'rejected'),

            (george_user := User.objects.get(username='george'), 'DevOps Engineer', 'TechCorp Kazakhstan',
             'DevOps 3 года. Docker, Kubernetes, Terraform, AWS. Автоматизировал CI/CD на прошлом месте.', 'pending'),

            (fatima, 'Data Analyst', 'TechCorp Kazakhstan',
             'Data Science студентка, работаю с Pandas и SQL каждый день. Хочу в аналитику!', 'pending'),
            (alice, 'Data Analyst', 'TechCorp Kazakhstan',
             'Знаю Python и SQL, интересуюсь аналитикой данных. Готова учиться BI-инструментам.', 'pending'),

            (marat, 'Junior Mobile Developer (Flutter)', 'TechCorp Kazakhstan',
             'Изучаю Flutter, сделал пару учебных приложений. Хочу в мобильную разработку!', 'pending'),

            (julia, 'Стажёр Frontend-разработчик', 'TechCorp Kazakhstan',
             'Очень хочу попасть на стажировку! Готова учиться круглосуточно.', 'reviewed'),
            (bob, 'Стажёр Frontend-разработчик', 'TechCorp Kazakhstan',
             'React + TypeScript — готов к стажировке.', 'pending'),

            # === Отклики на StartupX ===
            (alice, 'Fullstack Developer (Junior+)', 'StartupX',
             'Хочу попробовать fullstack! Python — основной язык, React изучаю.', 'pending'),
            (bob, 'Fullstack Developer (Junior+)', 'StartupX',
             'Готов учить backend! У меня сильный React, и я быстро осваиваю новое.', 'accepted'),
            (ivan, 'Mobile Developer (React Native)', 'StartupX',
             'React Native — мой основной инструмент. Публиковал приложения в обоих сторах.', 'reviewed'),
            (marat, 'Junior Python Developer (Remote)', 'StartupX',
             'Хочу удалённую работу! Python учу уже год, есть pet-проекты.', 'pending'),

            # === Отклики на DataFlow ===
            (fatima, 'Junior Data Analyst', 'DataFlow Analytics',
             'Data Science студентка, работаю с Pandas и SQL. Интересуюсь ML.', 'pending'),
            (charlie, 'Middle Data Engineer', 'DataFlow Analytics',
             'Хочу перейти в data engineering. Знаю Python, SQL, Docker.', 'pending'),
            (erik, 'Senior ML Engineer', 'DataFlow Analytics',
             'Опыт с ML/DL, PyTorch, MLOps. Готов лидировать направление.', 'reviewed'),
        ]

        for item in apps:
            user, job_title, company, cover, status = item
            job = get_job(job_title, company)
            if job:
                Application.objects.get_or_create(
                    applicant=user, job=job,
                    defaults={'cover_letter': cover, 'status': status})

        # Favorites
        for user in [alice, bob, charlie, fatima, julia, marat, nastya]:
            for job in list(Job.objects.order_by('?')[:4]):
                Favorite.objects.get_or_create(user=user, job=job)

        self.stdout.write(f'    Applications: {Application.objects.count()}')
        self.stdout.write(f'    Favorites: {Favorite.objects.count()}')
