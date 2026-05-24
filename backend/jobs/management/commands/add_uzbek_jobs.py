from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from jobs.models import Job


class Command(BaseCommand):
    help = 'Добавляет вакансии в городах Узбекистана'

    def handle(self, *args, **options):
        # Get or create a user for posting jobs
        hr_user, created = User.objects.get_or_create(
            username='hr_uzbekistan',
            defaults={
                'email': 'hr@uzbekjobs.uz',
                'first_name': 'HR',
                'last_name': 'Uzbekistan'
            }
        )

        if created:
            hr_user.set_password('password123')
            hr_user.save()
            self.stdout.write(self.style.SUCCESS(f'Создан пользователь: {hr_user.username}'))

        uzbek_jobs = [
            {
                'title': 'Junior Python Developer',
                'company': 'UZINFOCOM',
                'location': 'Ташкент',
                'salary_min': 3000000,
                'salary_max': 5000000,
                'level': 'junior',
                'experience_years': 0,
                'is_remote': False,
                'training_provided': True,
                'tech_stack': ['Python', 'Django', 'PostgreSQL', 'Git'],
                'description': 'Ищем начинающего Python разработчика для работы над государственными проектами. Обучение предоставляется. Работа в офисе в центре Ташкента.',
                'requirements_text': 'Базовые знания Python, желание учиться, знание русского и узбекского языков',
            },
            {
                'title': 'Frontend Developer (React)',
                'company': 'Click',
                'location': 'Ташкент',
                'salary_min': 5000000,
                'salary_max': 8000000,
                'level': 'mid',
                'experience_years': 2,
                'is_remote': True,
                'training_provided': False,
                'tech_stack': ['React', 'TypeScript', 'Redux', 'Tailwind CSS', 'Webpack'],
                'description': 'Click - ведущая платежная система Узбекистана. Разрабатываем мобильные и веб приложения для миллионов пользователей. Удаленная работа возможна.',
                'requirements_text': 'Опыт работы с React 2+ года, TypeScript, Redux, адаптивная верстка, знание английского языка',
            },
            {
                'title': 'Junior Java Developer',
                'company': 'Uzum',
                'location': 'Ташкент',
                'salary_min': 4000000,
                'salary_max': 6000000,
                'level': 'junior',
                'experience_years': 1,
                'is_remote': False,
                'training_provided': True,
                'tech_stack': ['Java', 'Spring Boot', 'PostgreSQL', 'Docker', 'Kafka'],
                'description': 'Uzum Market - крупнейший маркетплейс Узбекистана. Ищем Java разработчиков для backend команды. Менторство и обучение гарантируются.',
                'requirements_text': 'Знание Java, Spring Framework, SQL. Опыт работы от 1 года приветствуется',
            },
            {
                'title': 'Mobile Developer (Flutter)',
                'company': 'Payme',
                'location': 'Ташкент',
                'salary_min': 6000000,
                'salary_max': 10000000,
                'level': 'mid',
                'experience_years': 2,
                'is_remote': True,
                'training_provided': False,
                'tech_stack': ['Flutter', 'Dart', 'REST API', 'Firebase', 'Git'],
                'description': 'Payme - популярное платежное приложение. Разрабатываем кросс-платформенное приложение на Flutter для iOS и Android.',
                'requirements_text': 'Опыт разработки на Flutter 2+ года, знание Dart, работа с REST API, публикация приложений в App Store и Google Play',
            },
            {
                'title': 'DevOps Engineer',
                'company': 'EPAM Uzbekistan',
                'location': 'Ташкент',
                'salary_min': 8000000,
                'salary_max': 12000000,
                'level': 'mid',
                'experience_years': 3,
                'is_remote': True,
                'training_provided': False,
                'tech_stack': ['Docker', 'Kubernetes', 'AWS', 'Terraform', 'Jenkins', 'Linux'],
                'description': 'EPAM - международная IT компания с офисом в Ташкенте. Работаем с клиентами по всему миру. Ищем DevOps инженера для международных проектов.',
                'requirements_text': 'Опыт работы с Docker, Kubernetes, облачными платформами (AWS/Azure), CI/CD, scripting (Python/Bash), английский язык обязателен',
            },
            {
                'title': 'Junior PHP Developer',
                'company': 'Alijahon.uz',
                'location': 'Ташкент',
                'salary_min': 3500000,
                'salary_max': 5500000,
                'level': 'junior',
                'experience_years': 1,
                'is_remote': False,
                'training_provided': True,
                'tech_stack': ['PHP', 'Laravel', 'MySQL', 'Vue.js', 'Git'],
                'description': 'Интернет-магазин Alijahon.uz ищет PHP разработчика для поддержки и развития платформы. Обучение и рост внутри компании.',
                'requirements_text': 'Базовые знания PHP, желательно опыт с Laravel, MySQL, основы HTML/CSS/JavaScript',
            },
            {
                'title': 'QA Engineer (Automation)',
                'company': 'Humans',
                'location': 'Ташкент',
                'salary_min': 5000000,
                'salary_max': 7000000,
                'level': 'mid',
                'experience_years': 2,
                'is_remote': True,
                'training_provided': False,
                'tech_stack': ['Selenium', 'Python', 'Pytest', 'Postman', 'Jenkins', 'Git'],
                'description': 'Humans - аутсорсинговая IT компания. Разрабатываем решения для зарубежных клиентов. Ищем QA automation engineer.',
                'requirements_text': 'Опыт автоматизации тестирования 2+ года, знание Selenium/Pytest, тестирование API, английский язык',
            },
            {
                'title': 'Data Analyst',
                'company': 'Iman',
                'location': 'Ташкент',
                'salary_min': 4000000,
                'salary_max': 7000000,
                'level': 'junior',
                'experience_years': 1,
                'is_remote': False,
                'training_provided': True,
                'tech_stack': ['Python', 'SQL', 'Excel', 'Power BI', 'Pandas'],
                'description': 'Iman - финтех компания. Ищем аналитика данных для работы с большими данными и построения отчетов для бизнеса.',
                'requirements_text': 'Знание SQL, Python (Pandas), Excel на продвинутом уровне, базовые знания статистики',
            },
            {
                'title': 'UI/UX Designer',
                'company': 'Mediapark',
                'location': 'Ташкент',
                'salary_min': 4500000,
                'salary_max': 7500000,
                'level': 'mid',
                'experience_years': 2,
                'is_remote': True,
                'training_provided': False,
                'tech_stack': ['Figma', 'Adobe XD', 'Photoshop', 'Illustrator', 'Prototyping'],
                'description': 'Digital агентство Mediapark разрабатывает веб и мобильные приложения. Ищем креативного UI/UX дизайнера в команду.',
                'requirements_text': 'Портфолио с проектами, опыт работы с Figma, понимание UX принципов, создание прототипов',
            },
            {
                'title': 'Fullstack Developer (Node.js + React)',
                'company': 'Workly',
                'location': 'Ташкент',
                'salary_min': 7000000,
                'salary_max': 11000000,
                'level': 'mid',
                'experience_years': 3,
                'is_remote': True,
                'training_provided': False,
                'tech_stack': ['Node.js', 'React', 'MongoDB', 'Express', 'Redux', 'Docker'],
                'description': 'Workly - HR tech стартап. Создаем платформу для управления персоналом. Ищем fullstack разработчика.',
                'requirements_text': 'Опыт с Node.js и React 3+ года, знание MongoDB, REST API, опыт работы в стартапах приветствуется',
            },
            {
                'title': 'Junior Python Developer (Стажировка)',
                'company': 'PDP Academy',
                'location': 'Ташкент',
                'salary_min': 2000000,
                'salary_max': 3000000,
                'level': 'junior',
                'experience_years': 0,
                'is_remote': False,
                'training_provided': True,
                'tech_stack': ['Python', 'Django', 'DRF', 'PostgreSQL', 'Git', 'Docker'],
                'description': 'PDP Academy - IT образовательная платформа. Предлагаем стажировку для выпускников курсов. Менторство и реальные проекты.',
                'requirements_text': 'Базовые знания Python и Django, завершенные курсы по программированию, мотивация к обучению',
            },
            {
                'title': 'System Administrator',
                'company': 'UzCard',
                'location': 'Ташкент',
                'salary_min': 5000000,
                'salary_max': 8000000,
                'level': 'mid',
                'experience_years': 2,
                'is_remote': False,
                'training_provided': False,
                'tech_stack': ['Linux', 'Windows Server', 'VMware', 'Networking', 'Bash', 'PowerShell'],
                'description': 'UzCard - национальная платежная система. Ищем системного администратора для поддержки IT инфраструктуры.',
                'requirements_text': 'Опыт администрирования Linux/Windows серверов, знание сетевых технологий, виртуализация (VMware)',
            },
        ]

        created_count = 0
        for job_data in uzbek_jobs:
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                company=job_data['company'],
                posted_by=hr_user,
                defaults=job_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'[+] Создана вакансия: {job.title} в {job.company} ({job.location})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'[!] Вакансия уже существует: {job.title} в {job.company}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n[OK] Создано вакансий: {created_count} из {len(uzbek_jobs)}'
            )
        )
