import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from jobs.models import Job
from tests_system.models import SkillTest, Question

# Create users
hr_user, _ = User.objects.get_or_create(
    username='hr1',
    defaults={'email': 'hr@test.com', 'first_name': 'Ivan', 'last_name': 'Petrov'}
)
if _:
    hr_user.set_password('test1234')
    hr_user.save()
    UserProfile.objects.create(user=hr_user, role='hr', company_name='TechCorp',
                               company_description='We are hiring!')

applicant_user, _ = User.objects.get_or_create(
    username='john',
    defaults={'email': 'john@test.com', 'first_name': 'John', 'last_name': 'Doe'}
)
if _:
    applicant_user.set_password('test1234')
    applicant_user.save()
    UserProfile.objects.create(user=applicant_user, role='applicant', level='junior',
                               skills=['Python', 'JavaScript', 'SQL'],
                               portfolio_url='https://portfolio.com',
                               github_url='https://github.com/john')

# Create jobs
jobs_data = [
    {
        'title': 'Junior Python Developer',
        'company': 'TechCorp',
        'location': 'Алматы',
        'level': 'junior',
        'salary_min': 500000,
        'salary_max': 800000,
        'experience_years': 1,
        'is_remote': False,
        'training_provided': True,
        'description': 'Ищем junior разработчика Python для работы с Django. Обучение предоставляется.',
        'requirements_text': 'Базовое знание Python, желательно Django. Коммуникабельность.',
        'tech_stack': ['Python', 'Django', 'PostgreSQL', 'Git'],
        'posted_by': hr_user,
    },
    {
        'title': 'Mid-level React Developer',
        'company': 'WebStudio',
        'location': 'Нур-Султан',
        'level': 'mid',
        'salary_min': 1200000,
        'salary_max': 1800000,
        'experience_years': 3,
        'is_remote': True,
        'training_provided': False,
        'description': 'Требуется опытный React разработчик для фронтенда. Удалённая работа.',
        'requirements_text': '3+ лет опыта с React, знание TypeScript, REST API.',
        'tech_stack': ['React', 'TypeScript', 'Redux', 'Jest'],
        'posted_by': hr_user,
    },
    {
        'title': 'Senior Backend Developer',
        'company': 'CloudSys',
        'location': 'Астана',
        'level': 'senior',
        'salary_min': 2500000,
        'salary_max': 4000000,
        'experience_years': 5,
        'is_remote': True,
        'training_provided': False,
        'description': 'Опытный бэкенд разработчик для архитектуры микросервисов.',
        'requirements_text': '5+ лет, опыт с Go/Python, микросервисы, Docker, Kubernetes.',
        'tech_stack': ['Go', 'Docker', 'Kubernetes', 'PostgreSQL', 'Redis'],
        'posted_by': hr_user,
    },
    {
        'title': 'Junior JavaScript Developer',
        'company': 'StartupXYZ',
        'location': 'Онлайн',
        'level': 'junior',
        'salary_min': 600000,
        'salary_max': 900000,
        'experience_years': 0,
        'is_remote': True,
        'training_provided': True,
        'description': 'Начинаем с нуля! Полное обучение и менторство для новичков в JS.',
        'requirements_text': 'Готовность учиться, базовое программирование, логическое мышление.',
        'tech_stack': ['JavaScript', 'Node.js', 'Express'],
        'posted_by': hr_user,
    },
]

for job_data in jobs_data:
    job, created = Job.objects.get_or_create(
        title=job_data['title'],
        company=job_data['company'],
        defaults=job_data
    )
    if created:
        print(f"✓ Created: {job.title}")

# Create tests
tests_data = [
    {
        'title': 'Python Basics',
        'description': 'Test your Python knowledge',
        'language': 'python',
        'difficulty': 'easy',
    },
    {
        'title': 'Django ORM',
        'description': 'Test Django ORM concepts',
        'language': 'python',
        'difficulty': 'medium',
    },
    {
        'title': 'React Hooks',
        'description': 'Test your React hooks knowledge',
        'language': 'react',
        'difficulty': 'medium',
    },
    {
        'title': 'JavaScript Advanced',
        'description': 'Test advanced JavaScript',
        'language': 'javascript',
        'difficulty': 'hard',
    },
]

for test_data in tests_data:
    test, created = SkillTest.objects.get_or_create(
        title=test_data['title'],
        defaults=test_data
    )
    if created:
        # Add sample questions
        questions = [
            {'text': 'What is Python?', 'option_a': 'Programming language', 'option_b': 'Snake', 'option_c': 'Food', 'option_d': 'None', 'correct_answer': 'a', 'question_type': 'quiz'},
            {'text': 'What is 2 + 2?', 'option_a': '3', 'option_b': '4', 'option_c': '5', 'option_d': '6', 'correct_answer': 'b', 'question_type': 'quiz'},
        ]
        for q in questions:
            Question.objects.get_or_create(test=test, text=q['text'], defaults=q)
        print(f"✓ Created test: {test.title}")

print("\n✅ Data loaded successfully!")
print(f"HR User: hr1 / test1234")
print(f"Applicant: john / test1234")
