# 🏗️ JobPlatform Architecture - Global AI Platform

## Выбранные модули для реализации:

1. **AI-Powered Platform** (все компоненты A, B, C, D)
2. **Global Talent Marketplace** (C: Legal & Compliance, D: Локализация)
7. **Data & Analytics Platform** (A: Market Intelligence)
8. **Social Network** (A: Professional Networking)

---

## 🎯 ФАЗА 1: Фундамент (2 месяца)

### 1.1 Backend Infrastructure

```
New Django Apps:
├── ai_engine/           # AI модуль
│   ├── resume_parser.py
│   ├── matching.py
│   ├── assistant.py
│   └── interview_coach.py
├── international/       # Международная экспансия
│   ├── currencies.py
│   ├── legal_templates.py
│   └── localization.py
├── analytics/          # ✅ Уже есть - расширить
│   ├── market_intelligence.py
│   ├── salary_benchmarks.py
│   └── trends.py
└── social/             # Профессиональная сеть
    ├── connections.py
    ├── endorsements.py
    └── feed.py
```

### 1.2 Database Schema Extensions

```sql
-- AI Engine Tables
CREATE TABLE ai_resume_analysis (
    id SERIAL PRIMARY KEY,
    user_profile_id INT REFERENCES accounts_userprofile(id),
    resume_file TEXT,
    parsed_data JSONB,
    extracted_skills TEXT[],
    detected_level VARCHAR(10),
    confidence_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ai_job_matches (
    id SERIAL PRIMARY KEY,
    user_profile_id INT REFERENCES accounts_userprofile(id),
    job_id INT REFERENCES jobs_job(id),
    match_score DECIMAL(5,2),
    match_reasons JSONB,
    semantic_similarity DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ai_chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES auth_user(id),
    session_type VARCHAR(20), -- 'assistant', 'interview_coach'
    messages JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- International Tables
CREATE TABLE supported_currencies (
    id SERIAL PRIMARY KEY,
    code VARCHAR(3) UNIQUE, -- USD, EUR, UZS
    symbol VARCHAR(10),
    exchange_rate DECIMAL(10,4),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE legal_templates (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(2),
    template_type VARCHAR(50), -- 'contract', 'nda', 'work_permit'
    content TEXT,
    language VARCHAR(5),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Analytics Tables
CREATE TABLE salary_benchmarks (
    id SERIAL PRIMARY KEY,
    job_title VARCHAR(255),
    level VARCHAR(10),
    city VARCHAR(100),
    country VARCHAR(2),
    currency VARCHAR(3),
    min_salary INT,
    max_salary INT,
    median_salary INT,
    sample_size INT,
    quarter VARCHAR(7), -- '2026-Q1'
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE market_trends (
    id SERIAL PRIMARY KEY,
    skill_name VARCHAR(100),
    demand_score INT, -- 0-100
    growth_rate DECIMAL(5,2), -- % change
    avg_salary DECIMAL(10,2),
    job_count INT,
    period VARCHAR(7),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Social Network Tables
CREATE TABLE user_connections (
    id SERIAL PRIMARY KEY,
    from_user_id INT REFERENCES auth_user(id),
    to_user_id INT REFERENCES auth_user(id),
    status VARCHAR(20), -- 'pending', 'accepted', 'blocked'
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(from_user_id, to_user_id)
);

CREATE TABLE skill_endorsements (
    id SERIAL PRIMARY KEY,
    user_profile_id INT REFERENCES accounts_userprofile(id),
    skill_name VARCHAR(100),
    endorsed_by_id INT REFERENCES auth_user(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_profile_id, skill_name, endorsed_by_id)
);

CREATE TABLE user_posts (
    id SERIAL PRIMARY KEY,
    author_id INT REFERENCES auth_user(id),
    content TEXT,
    post_type VARCHAR(20), -- 'article', 'update', 'achievement'
    media_urls TEXT[],
    likes_count INT DEFAULT 0,
    comments_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE post_reactions (
    id SERIAL PRIMARY KEY,
    post_id INT REFERENCES user_posts(id),
    user_id INT REFERENCES auth_user(id),
    reaction_type VARCHAR(20), -- 'like', 'celebrate', 'insightful'
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(post_id, user_id)
);
```

### 1.3 External Services Setup

```python
# requirements.txt additions

# AI & ML
openai==1.12.0
langchain==0.1.10
sentence-transformers==2.5.1
PyPDF2==3.0.1
python-docx==1.1.0
spacy==3.7.4

# Analytics
pandas==2.2.1
numpy==1.26.4
plotly==5.19.0

# International
forex-python==1.8
babel==2.14.0
pycountry==23.12.11

# Caching & Performance
redis==5.0.1
celery==5.3.6

# File Storage
boto3==1.34.51  # AWS S3 для резюме
```

---

## 🤖 ФАЗА 2: AI Engine (Месяц 2-4)

### 2.1 AI Resume Parser

**Компоненты:**
```python
# ai_engine/resume_parser.py

import openai
from PyPDF2 import PdfReader
from docx import Document
import json

class ResumeParser:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def parse_pdf(self, file_path):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    
    def parse_docx(self, file_path):
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    
    def extract_structured_data(self, resume_text):
        """
        Использует GPT-4 для извлечения структурированных данных
        """
        prompt = f"""
        Extract the following information from this resume in JSON format:
        
        {{
            "name": "",
            "email": "",
            "phone": "",
            "location": "",
            "skills": [],
            "experience": [
                {{
                    "company": "",
                    "position": "",
                    "duration": "",
                    "description": ""
                }}
            ],
            "education": [
                {{
                    "institution": "",
                    "degree": "",
                    "field": "",
                    "year": ""
                }}
            ],
            "detected_level": "junior|mid|senior",
            "years_of_experience": 0
        }}
        
        Resume text:
        {resume_text}
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional resume parser."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
    
    def auto_fill_profile(self, user_profile, parsed_data):
        """
        Автоматически заполняет профиль пользователя
        """
        user_profile.skills = parsed_data.get('skills', [])
        user_profile.level = parsed_data.get('detected_level', 'junior')
        user_profile.bio = parsed_data.get('summary', '')
        user_profile.save()
        
        return user_profile
```

**API Endpoints:**
```python
# POST /api/ai/parse-resume/
{
    "file": <uploaded_file>
}

# Response:
{
    "parsed_data": {
        "name": "John Doe",
        "email": "john@example.com",
        "skills": ["Python", "Django", "React"],
        "detected_level": "mid",
        "years_of_experience": 3
    },
    "auto_fill_available": true
}
```

### 2.2 Semantic Job Matching

**Компоненты:**
```python
# ai_engine/matching.py

from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SemanticMatcher:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def create_profile_embedding(self, user_profile):
        """
        Создает vector representation профиля
        """
        profile_text = f"""
        Level: {user_profile.level}
        Skills: {', '.join(user_profile.skills)}
        Bio: {user_profile.bio}
        Experience: {user_profile.years_experience} years
        """
        return self.model.encode(profile_text)
    
    def create_job_embedding(self, job):
        """
        Создает vector representation вакансии
        """
        job_text = f"""
        Title: {job.title}
        Level: {job.level}
        Requirements: {job.requirements_text}
        Tech Stack: {', '.join(job.tech_stack)}
        Description: {job.description}
        """
        return self.model.encode(job_text)
    
    def calculate_match_score(self, profile_embedding, job_embedding):
        """
        Вычисляет similarity score 0-100
        """
        similarity = cosine_similarity(
            profile_embedding.reshape(1, -1),
            job_embedding.reshape(1, -1)
        )[0][0]
        
        # Convert to 0-100 scale
        return round(similarity * 100, 2)
    
    def get_match_reasons(self, user_profile, job):
        """
        Объясняет почему вакансия подходит (используя GPT)
        """
        prompt = f"""
        Explain in 2-3 bullet points why this job matches the candidate:
        
        Candidate:
        - Level: {user_profile.level}
        - Skills: {', '.join(user_profile.skills)}
        
        Job:
        - Title: {job.title}
        - Level: {job.level}
        - Required skills: {', '.join(job.tech_stack)}
        
        Be specific and positive. Format as JSON array of strings.
        """
        
        # GPT call here...
        return [
            "Your Python and Django skills match perfectly",
            "The junior level aligns with your experience",
            "Remote work option fits your preference"
        ]
    
    def find_best_matches(self, user_profile, limit=10):
        """
        Находит топ подходящих вакансий
        """
        profile_emb = self.create_profile_embedding(user_profile)
        
        jobs = Job.objects.filter(is_active=True)
        matches = []
        
        for job in jobs:
            job_emb = self.create_job_embedding(job)
            score = self.calculate_match_score(profile_emb, job_emb)
            
            if score > 50:  # Threshold
                matches.append({
                    'job': job,
                    'score': score,
                    'reasons': self.get_match_reasons(user_profile, job)
                })
        
        # Sort by score
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:limit]
```

**API Endpoints:**
```python
# GET /api/ai/job-recommendations/
{
    "matches": [
        {
            "job_id": 123,
            "title": "Junior Python Developer",
            "company": "TechCorp",
            "match_score": 87.5,
            "reasons": [
                "Your Python and Django skills match perfectly",
                "The junior level aligns with your experience"
            ]
        }
    ]
}
```

### 2.3 AI Career Assistant

**Компоненты:**
```python
# ai_engine/assistant.py

class CareerAssistant:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.conversation_history = []
    
    def chat(self, user_message, user_profile):
        """
        Чат-бот для карьерных советов
        """
        system_prompt = f"""
        You are a professional career advisor for IT professionals in Uzbekistan.
        
        User context:
        - Level: {user_profile.level}
        - Skills: {', '.join(user_profile.skills)}
        - Looking for: {user_profile.preferred_job_type}
        
        Provide helpful, specific advice. Be encouraging and practical.
        """
        
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                *self.conversation_history
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        assistant_message = response.choices[0].message.content
        
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    def generate_cover_letter(self, user_profile, job):
        """
        Генерирует сопроводительное письмо
        """
        prompt = f"""
        Write a professional cover letter for this job application:
        
        Candidate:
        - Name: {user_profile.user.get_full_name()}
        - Level: {user_profile.level}
        - Skills: {', '.join(user_profile.skills)}
        - Bio: {user_profile.bio}
        
        Job:
        - Company: {job.company}
        - Title: {job.title}
        - Requirements: {job.requirements_text}
        
        Make it professional, concise (150-200 words), and enthusiastic.
        Highlight relevant skills. Write in Russian.
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional cover letter writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def suggest_skills_to_learn(self, user_profile):
        """
        Рекомендует навыки для изучения
        """
        prompt = f"""
        Based on this profile, suggest 3-5 skills to learn next for career growth:
        
        Current level: {user_profile.level}
        Current skills: {', '.join(user_profile.skills)}
        
        Consider:
        - Market demand in Uzbekistan
        - Natural progression for their level
        - Complementary skills
        
        Format as JSON array with skill name and reason.
        """
        
        # GPT call...
        return [
            {
                "skill": "Docker",
                "reason": "High demand for containerization, complements your backend skills"
            },
            {
                "skill": "React",
                "reason": "Frontend skills make you full-stack, increases opportunities"
            }
        ]
```

**API Endpoints:**
```python
# POST /api/ai/assistant/chat/
{
    "message": "Как улучшить мое резюме?"
}

# Response:
{
    "response": "Для улучшения резюме рекомендую...",
    "suggestions": ["add_projects", "highlight_achievements"]
}

# POST /api/ai/generate-cover-letter/
{
    "job_id": 123
}

# Response:
{
    "cover_letter": "Уважаемые представители компании..."
}
```

### 2.4 AI Interview Coach

```python
# ai_engine/interview_coach.py

class InterviewCoach:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_interview_questions(self, job):
        """
        Генерирует вопросы для собеседования
        """
        prompt = f"""
        Generate 10 interview questions for this position:
        
        Title: {job.title}
        Level: {job.level}
        Tech Stack: {', '.join(job.tech_stack)}
        Requirements: {job.requirements_text}
        
        Include:
        - 3 technical questions
        - 3 behavioral questions
        - 2 problem-solving scenarios
        - 2 company-specific questions
        
        Format as JSON array with question and expected answer outline.
        """
        
        # GPT call...
        return [
            {
                "question": "Explain the difference between REST and GraphQL",
                "type": "technical",
                "difficulty": "medium",
                "answer_outline": "Should mention: request structure, over/under fetching..."
            }
        ]
    
    def evaluate_answer(self, question, user_answer):
        """
        Оценивает ответ кандидата
        """
        prompt = f"""
        Evaluate this interview answer:
        
        Question: {question}
        Answer: {user_answer}
        
        Provide:
        - Score (0-10)
        - Strengths
        - Areas for improvement
        - Suggested better answer
        
        Format as JSON.
        """
        
        # GPT call...
        return {
            "score": 7,
            "strengths": ["Good structure", "Mentioned key concepts"],
            "improvements": ["Could add more examples", "Expand on GraphQL subscriptions"],
            "suggested_answer": "A more complete answer would be..."
        }
    
    def conduct_mock_interview(self, user_profile, job_id):
        """
        Проводит мок-интервью
        """
        job = Job.objects.get(id=job_id)
        questions = self.generate_interview_questions(job)
        
        return {
            "session_id": "mock_123",
            "questions": questions,
            "instructions": "Answer each question. You'll get feedback after."
        }
```

---

## 🌍 ФАЗА 3: International (Месяц 4-5)

### 3.1 Multi-Currency System

```python
# international/currencies.py

from forex_python.converter import CurrencyRates
from decimal import Decimal

class CurrencyManager:
    def __init__(self):
        self.cr = CurrencyRates()
        self.base_currency = 'UZS'
    
    def update_exchange_rates(self):
        """
        Обновляет курсы валют (Celery task, каждые 6 часов)
        """
        currencies = ['USD', 'EUR', 'RUB', 'KZT', 'UZS']
        
        for currency in currencies:
            if currency != self.base_currency:
                rate = self.cr.get_rate(currency, self.base_currency)
                
                SupportedCurrency.objects.update_or_create(
                    code=currency,
                    defaults={
                        'exchange_rate': Decimal(str(rate)),
                        'updated_at': timezone.now()
                    }
                )
    
    def convert(self, amount, from_currency, to_currency):
        """
        Конвертирует сумму между валютами
        """
        if from_currency == to_currency:
            return amount
        
        from_rate = SupportedCurrency.objects.get(code=from_currency).exchange_rate
        to_rate = SupportedCurrency.objects.get(code=to_currency).exchange_rate
        
        # Convert to base currency, then to target
        base_amount = amount * from_rate
        return base_amount / to_rate
    
    def format_salary(self, amount, currency):
        """
        Форматирует зарплату с правильным символом
        """
        symbols = {
            'USD': '$',
            'EUR': '€',
            'UZS': 'сўм',
            'RUB': '₽',
            'KZT': '₸'
        }
        
        symbol = symbols.get(currency, currency)
        
        if amount >= 1000000:
            return f"{amount/1000000:.1f}M {symbol}"
        elif amount >= 1000:
            return f"{amount/1000:.0f}K {symbol}"
        else:
            return f"{amount:,.0f} {symbol}"
```

**Database Updates:**
```sql
-- Add currency fields to jobs
ALTER TABLE jobs_job 
ADD COLUMN salary_currency VARCHAR(3) DEFAULT 'UZS',
ADD COLUMN salary_min_usd DECIMAL(10,2),
ADD COLUMN salary_max_usd DECIMAL(10,2);

-- Create index for currency conversions
CREATE INDEX idx_jobs_currency ON jobs_job(salary_currency);
```

### 3.2 Legal Templates

```python
# international/legal_templates.py

class LegalTemplateManager:
    TEMPLATE_TYPES = {
        'employment_contract': 'Employment Contract',
        'nda': 'Non-Disclosure Agreement',
        'independent_contractor': 'Independent Contractor Agreement',
        'work_permit': 'Work Permit Application'
    }
    
    def get_template(self, country_code, template_type, language='en'):
        """
        Получает юридический шаблон
        """
        template = LegalTemplate.objects.filter(
            country_code=country_code,
            template_type=template_type,
            language=language
        ).first()
        
        if not template:
            # Fallback to default
            template = LegalTemplate.objects.filter(
                country_code='INTL',
                template_type=template_type,
                language='en'
            ).first()
        
        return template
    
    def fill_template(self, template, context):
        """
        Заполняет шаблон данными
        """
        content = template.content
        
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        
        return content
    
    def generate_contract(self, application, contract_type='employment_contract'):
        """
        Генерирует контракт для заявки
        """
        job = application.job
        applicant = application.applicant
        
        template = self.get_template(
            country_code='UZ',
            template_type=contract_type,
            language='ru'
        )
        
        context = {
            'employer_name': job.company,
            'employee_name': applicant.get_full_name(),
            'position': job.title,
            'salary': f"{job.salary_min}-{job.salary_max} {job.salary_currency}",
            'start_date': timezone.now().date(),
            'location': job.location
        }
        
        return self.fill_template(template, context)
```

**Sample Templates:**
```markdown
# templates/contracts/UZ_employment_contract_ru.md

ТРУДОВОЙ ДОГОВОР

г. {{location}}, {{current_date}}

{{employer_name}} (далее - Работодатель) 
и 
{{employee_name}} (далее - Работник)

заключили настоящий договор о нижеследующем:

1. ПРЕДМЕТ ДОГОВОРА
1.1. Работник принимается на должность {{position}}
1.2. Место работы: {{location}}
1.3. Заработная плата: {{salary}}

2. ОБЯЗАННОСТИ СТОРОН
...

[Full template with all legal clauses]
```

### 3.3 Localization

```python
# international/localization.py

from django.utils.translation import gettext as _
from babel.numbers import format_currency
import pycountry

class LocalizationManager:
    SUPPORTED_LANGUAGES = {
        'ru': 'Русский',
        'uz': 'O\'zbekcha',
        'en': 'English'
    }
    
    SUPPORTED_COUNTRIES = {
        'UZ': 'Uzbekistan',
        'KZ': 'Kazakhstan',
        'RU': 'Russia',
        'US': 'United States',
        'GB': 'United Kingdom'
    }
    
    def get_country_info(self, country_code):
        """
        Получает информацию о стране
        """
        country = pycountry.countries.get(alpha_2=country_code)
        
        return {
            'code': country.alpha_2,
            'name': country.name,
            'currency': self.get_country_currency(country_code),
            'languages': self.get_country_languages(country_code),
            'timezone': self.get_country_timezone(country_code)
        }
    
    def localize_job_listing(self, job, target_country, target_language):
        """
        Адаптирует вакансию для целевой страны
        """
        # Translate title and description
        translated_title = self.translate(job.title, target_language)
        translated_desc = self.translate(job.description, target_language)
        
        # Convert salary
        currency_manager = CurrencyManager()
        target_currency = self.get_country_currency(target_country)
        
        salary_min_local = currency_manager.convert(
            job.salary_min,
            job.salary_currency,
            target_currency
        )
        
        return {
            'title': translated_title,
            'description': translated_desc,
            'salary_min': salary_min_local,
            'salary_currency': target_currency,
            'formatted_salary': currency_manager.format_salary(
                salary_min_local,
                target_currency
            )
        }
```

---

## 📊 ФАЗА 4: Analytics Platform (Месяц 5-6)

### 4.1 Market Intelligence

```python
# analytics/market_intelligence.py

class MarketIntelligence:
    def generate_salary_benchmarks(self):
        """
        Генерирует salary benchmarks из реальных данных
        """
        current_quarter = f"{timezone.now().year}-Q{(timezone.now().month-1)//3+1}"
        
        # Aggregate data
        benchmarks = Job.objects.filter(
            is_active=True,
            created_at__gte=timezone.now() - timedelta(days=90)
        ).values(
            'title', 'level', 'location'
        ).annotate(
            min_salary=Min('salary_min'),
            max_salary=Max('salary_max'),
            median_salary=Avg('salary_min'),
            count=Count('id')
        )
        
        for benchmark in benchmarks:
            SalaryBenchmark.objects.create(
                job_title=benchmark['title'],
                level=benchmark['level'],
                city=benchmark['location'],
                country='UZ',
                currency='UZS',
                min_salary=benchmark['min_salary'],
                max_salary=benchmark['max_salary'],
                median_salary=benchmark['median_salary'],
                sample_size=benchmark['count'],
                quarter=current_quarter
            )
    
    def get_trending_skills(self):
        """
        Определяет трендовые навыки
        """
        # Count skill occurrences in recent jobs
        skill_counts = {}
        
        jobs = Job.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        )
        
        for job in jobs:
            for skill in job.tech_stack:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Calculate growth rate compared to previous period
        trending = []
        
        for skill, count in skill_counts.items():
            prev_count = self.get_previous_period_count(skill)
            growth_rate = ((count - prev_count) / prev_count * 100) if prev_count > 0 else 100
            
            trending.append({
                'skill': skill,
                'count': count,
                'growth_rate': round(growth_rate, 2)
            })
        
        # Sort by growth rate
        trending.sort(key=lambda x: x['growth_rate'], reverse=True)
        
        return trending[:10]
    
    def generate_market_report(self, quarter):
        """
        Генерирует квартальный отчет о рынке труда
        """
        report = {
            'quarter': quarter,
            'total_jobs': Job.objects.filter(
                created_at__year=timezone.now().year,
                created_at__month__gte=(quarter-1)*3+1,
                created_at__month__lte=quarter*3
            ).count(),
            'top_companies': self.get_top_hiring_companies(quarter),
            'salary_trends': self.get_salary_trends(quarter),
            'skill_demand': self.get_skill_demand(quarter),
            'level_distribution': self.get_level_distribution(quarter)
        }
        
        return report
    
    def predict_demand(self, skill, months_ahead=3):
        """
        Предсказывает будущий спрос на навык
        """
        # Simple linear regression on historical data
        historical_data = MarketTrend.objects.filter(
            skill_name=skill
        ).order_by('created_at')[:12]  # Last 12 months
        
        if len(historical_data) < 3:
            return None
        
        # Extract job counts
        x = list(range(len(historical_data)))
        y = [trend.job_count for trend in historical_data]
        
        # Simple linear regression
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # Predict future
        future_x = len(historical_data) + months_ahead
        predicted_count = slope * future_x + intercept
        
        return {
            'skill': skill,
            'current_demand': y[-1],
            'predicted_demand': round(predicted_count),
            'trend': 'growing' if slope > 0 else 'declining',
            'confidence': round(r_value ** 2, 2)
        }
```

**API Endpoints:**
```python
# GET /api/analytics/salary-benchmarks/
{
    "job_title": "Python Developer",
    "level": "mid",
    "city": "Ташкент",
    "benchmarks": {
        "min": 5000000,
        "max": 10000000,
        "median": 7500000,
        "currency": "UZS",
        "sample_size": 45,
        "quarter": "2026-Q2"
    }
}

# GET /api/analytics/trending-skills/
{
    "skills": [
        {
            "name": "React",
            "job_count": 156,
            "growth_rate": 45.2,
            "avg_salary": 8000000
        }
    ]
}

# GET /api/analytics/market-report/
{
    "quarter": "2026-Q2",
    "total_jobs": 1250,
    "top_companies": [...],
    "insights": [...]
}
```

---

## 👥 ФАЗА 5: Social Network (Месяц 6-7)

### 5.1 Professional Connections

```python
# social/connections.py

class ConnectionManager:
    def send_connection_request(self, from_user, to_user, message=''):
        """
        Отправляет запрос на связь
        """
        if from_user == to_user:
            raise ValueError("Cannot connect to yourself")
        
        # Check if connection already exists
        existing = UserConnection.objects.filter(
            Q(from_user=from_user, to_user=to_user) |
            Q(from_user=to_user, to_user=from_user)
        ).first()
        
        if existing:
            raise ValueError("Connection already exists")
        
        connection = UserConnection.objects.create(
            from_user=from_user,
            to_user=to_user,
            status='pending',
            message=message
        )
        
        # Send notification
        self.notify_connection_request(to_user, from_user)
        
        return connection
    
    def accept_connection(self, connection_id, user):
        """
        Принимает запрос на связь
        """
        connection = UserConnection.objects.get(id=connection_id)
        
        if connection.to_user != user:
            raise PermissionError("Not authorized")
        
        connection.status = 'accepted'
        connection.save()
        
        # Notify requester
        self.notify_connection_accepted(connection.from_user, user)
        
        return connection
    
    def get_connections(self, user):
        """
        Получает все связи пользователя
        """
        connections = UserConnection.objects.filter(
            Q(from_user=user) | Q(to_user=user),
            status='accepted'
        ).select_related('from_user', 'to_user', 'from_user__profile', 'to_user__profile')
        
        result = []
        for conn in connections:
            other_user = conn.to_user if conn.from_user == user else conn.from_user
            result.append({
                'user': other_user,
                'profile': other_user.profile,
                'connected_at': conn.created_at
            })
        
        return result
    
    def get_mutual_connections(self, user1, user2):
        """
        Находит общие связи
        """
        user1_connections = set(self.get_connection_ids(user1))
        user2_connections = set(self.get_connection_ids(user2))
        
        mutual_ids = user1_connections & user2_connections
        
        return User.objects.filter(id__in=mutual_ids)
    
    def suggest_connections(self, user, limit=10):
        """
        Рекомендует связи (People You May Know)
        """
        # Get user's connections
        user_connections = set(self.get_connection_ids(user))
        
        # Find connections of connections
        candidates = {}
        
        for conn_id in user_connections:
            conn = User.objects.get(id=conn_id)
            second_degree = self.get_connection_ids(conn)
            
            for candidate_id in second_degree:
                if candidate_id == user.id or candidate_id in user_connections:
                    continue
                
                candidates[candidate_id] = candidates.get(candidate_id, 0) + 1
        
        # Sort by mutual connections count
        sorted_candidates = sorted(
            candidates.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        result = []
        for user_id, mutual_count in sorted_candidates:
            candidate = User.objects.get(id=user_id)
            result.append({
                'user': candidate,
                'profile': candidate.profile,
                'mutual_connections': mutual_count
            })
        
        return result
```

### 5.2 Skill Endorsements

```python
# social/endorsements.py

class EndorsementManager:
    def endorse_skill(self, endorser, user_profile, skill_name):
        """
        Подтверждает навык пользователя
        """
        # Check if they're connected
        if not self.are_connected(endorser, user_profile.user):
            raise PermissionError("Can only endorse connections")
        
        # Check if already endorsed
        existing = SkillEndorsement.objects.filter(
            user_profile=user_profile,
            skill_name=skill_name,
            endorsed_by=endorser
        ).exists()
        
        if existing:
            raise ValueError("Already endorsed this skill")
        
        endorsement = SkillEndorsement.objects.create(
            user_profile=user_profile,
            skill_name=skill_name,
            endorsed_by=endorser
        )
        
        # Update skill count
        self.update_skill_endorsement_count(user_profile, skill_name)
        
        return endorsement
    
    def get_skill_endorsements(self, user_profile, skill_name):
        """
        Получает список кто подтвердил навык
        """
        endorsements = SkillEndorsement.objects.filter(
            user_profile=user_profile,
            skill_name=skill_name
        ).select_related('endorsed_by', 'endorsed_by__profile')
        
        return endorsements
    
    def get_top_endorsed_skills(self, user_profile):
        """
        Получает топ подтвержденных навыков
        """
        skills = SkillEndorsement.objects.filter(
            user_profile=user_profile
        ).values('skill_name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return skills
```

### 5.3 Professional Feed

```python
# social/feed.py

class FeedManager:
    def create_post(self, author, content, post_type='update', media_urls=None):
        """
        Создает пост в ленте
        """
        post = UserPost.objects.create(
            author=author,
            content=content,
            post_type=post_type,
            media_urls=media_urls or []
        )
        
        # Notify connections
        self.notify_connections_new_post(author, post)
        
        return post
    
    def get_feed(self, user, limit=20, offset=0):
        """
        Получает персонализированную ленту
        """
        # Get user's connections
        connection_ids = self.get_connection_ids(user)
        
        # Get posts from connections + own posts
        posts = UserPost.objects.filter(
            Q(author_id__in=connection_ids) | Q(author=user)
        ).select_related(
            'author', 'author__profile'
        ).order_by('-created_at')[offset:offset+limit]
        
        return posts
    
    def react_to_post(self, user, post_id, reaction_type='like'):
        """
        Реагирует на пост
        """
        post = UserPost.objects.get(id=post_id)
        
        reaction, created = PostReaction.objects.get_or_create(
            post=post,
            user=user,
            defaults={'reaction_type': reaction_type}
        )
        
        if not created:
            reaction.reaction_type = reaction_type
            reaction.save()
        else:
            # Increment counter
            post.likes_count += 1
            post.save()
        
        return reaction
    
    def generate_achievement_post(self, user, achievement_type, data):
        """
        Автоматически создает пост о достижении
        """
        templates = {
            'test_passed': "Успешно сдал тест '{test_name}' с результатом {score}%!",
            'job_accepted': "Рад объявить, что начинаю работать в {company} на позиции {title}!",
            'new_skill': "Освоил новый навык: {skill_name}",
            'anniversary': "Сегодня {years} лет как я в IT!",
        }
        
        template = templates.get(achievement_type, '')
        content = template.format(**data)
        
        return self.create_post(
            author=user,
            content=content,
            post_type='achievement'
        )
```

---

Это ОГРОМНЫЙ план! Хочешь продолжить с конкретной реализацией какой-то части? Или сначала создадим migration файлы и базовую структуру?