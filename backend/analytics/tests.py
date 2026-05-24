from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.test import TestCase
from accounts.models import UserProfile
from jobs.models import Job
from .models import Favorite
from .requirement_parser import parse_skills, extract_experience_years
from .skill_classifier import classify_skill, classify_skills, detect_level_from_skills
from .job_analyzer import analyze_job
from .recommendation_engine import calculate_match, generate_recommendation
from .comparison import compare_jobs


# --- Unit tests: requirement_parser ---


class ParseSkillsTest(TestCase):

    def test_basic_skills(self):
        text = 'We need Python, Django, and PostgreSQL experience'
        skills = parse_skills(text)
        self.assertIn('Python', skills)
        self.assertIn('Django', skills)
        self.assertIn('PostgreSQL', skills)

    def test_aliases(self):
        text = 'Must know React.js and Node.js'
        skills = parse_skills(text)
        self.assertIn('React', skills)
        self.assertIn('Node.js', skills)

    def test_case_insensitive(self):
        text = 'PYTHON and DOCKER required'
        skills = parse_skills(text)
        self.assertIn('Python', skills)
        self.assertIn('Docker', skills)

    def test_empty_text(self):
        self.assertEqual(parse_skills(''), [])
        self.assertEqual(parse_skills(None), [])

    def test_no_skills_found(self):
        text = 'We need a hardworking team player'
        skills = parse_skills(text)
        self.assertEqual(skills, [])

    def test_russian_keywords(self):
        text = 'знание микросервисы и паттерны проектирования обязательно'
        skills = parse_skills(text)
        self.assertIn('Microservices', skills)
        self.assertIn('Design Patterns', skills)

    def test_short_aliases_word_boundary(self):
        text = 'going forward with the algorithm'
        skills = parse_skills(text)
        self.assertNotIn('Go', skills)

    def test_go_standalone(self):
        text = 'Experience with Go and Rust'
        skills = parse_skills(text)
        self.assertIn('Go', skills)
        self.assertIn('Rust', skills)


class ExtractExperienceTest(TestCase):

    def test_years_pattern(self):
        self.assertEqual(extract_experience_years('3+ years of experience'), 3)
        self.assertEqual(extract_experience_years('5 years experience'), 5)

    def test_russian_pattern(self):
        self.assertEqual(extract_experience_years('от 3 лет опыта'), 3)
        self.assertEqual(extract_experience_years('не менее 2 лет'), 2)

    def test_range_pattern(self):
        result = extract_experience_years('3-5 years')
        self.assertIn(result, (3, 5))

    def test_no_experience(self):
        self.assertEqual(extract_experience_years('No experience required'), 0)

    def test_empty(self):
        self.assertEqual(extract_experience_years(''), 0)
        self.assertEqual(extract_experience_years(None), 0)


# --- Unit tests: skill_classifier ---


class SkillClassifierTest(TestCase):

    def test_junior_skills(self):
        self.assertEqual(classify_skill('HTML'), 'junior')
        self.assertEqual(classify_skill('CSS'), 'junior')
        self.assertEqual(classify_skill('Git'), 'junior')

    def test_mid_skills(self):
        self.assertEqual(classify_skill('React'), 'mid')
        self.assertEqual(classify_skill('Django'), 'mid')
        self.assertEqual(classify_skill('Docker'), 'mid')

    def test_senior_skills(self):
        self.assertEqual(classify_skill('Kubernetes'), 'senior')
        self.assertEqual(classify_skill('AWS'), 'senior')
        self.assertEqual(classify_skill('Microservices'), 'senior')

    def test_unknown_defaults_to_mid(self):
        self.assertEqual(classify_skill('SomeObscureTool'), 'mid')

    def test_classify_skills_groups(self):
        skills = ['HTML', 'React', 'Kubernetes']
        result = classify_skills(skills)
        self.assertEqual(result['junior'], ['HTML'])
        self.assertEqual(result['mid'], ['React'])
        self.assertEqual(result['senior'], ['Kubernetes'])

    def test_detect_level_junior(self):
        skills = ['HTML', 'CSS', 'JavaScript', 'Git']
        level = detect_level_from_skills(skills, experience_years=0)
        self.assertEqual(level, 'junior')

    def test_detect_level_mid(self):
        skills = ['Python', 'Django', 'Docker', 'PostgreSQL', 'React']
        level = detect_level_from_skills(skills, experience_years=2)
        self.assertEqual(level, 'mid')

    def test_detect_level_senior(self):
        skills = ['Python', 'Kubernetes', 'AWS', 'Microservices', 'Kafka', 'Terraform']
        level = detect_level_from_skills(skills, experience_years=5)
        self.assertEqual(level, 'senior')

    def test_detect_level_empty(self):
        self.assertEqual(detect_level_from_skills([], 0), 'junior')


# --- Unit tests: job_analyzer ---


class JobAnalyzerTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='hr', password='pass123')

    def test_honest_junior_job(self):
        job = Job.objects.create(
            title='Junior Web Dev', company='Corp',
            description='Learn on the job', posted_by=self.user,
            requirements_text='HTML, CSS, JavaScript, Git basics',
            level='junior', experience_years=0,
            tech_stack=['HTML', 'CSS', 'JavaScript'],
        )
        result = analyze_job(job)
        self.assertEqual(result['detected_level'], 'junior')
        self.assertFalse(result['is_overqualified'])
        self.assertGreaterEqual(result['honesty_score'], 80)

    def test_inflated_junior_job(self):
        job = Job.objects.create(
            title='Junior Python Dev', company='Corp',
            description='Looking for junior', posted_by=self.user,
            requirements_text='Python, Django, Docker, Kubernetes, AWS, React, Microservices, 5+ years',
            level='junior', experience_years=5,
            tech_stack=['Python', 'Django', 'Docker', 'AWS'],
        )
        result = analyze_job(job)
        self.assertEqual(result['detected_level'], 'senior')
        self.assertTrue(result['is_overqualified'])
        self.assertLess(result['honesty_score'], 30)

    def test_honest_senior_job(self):
        job = Job.objects.create(
            title='Senior Backend Engineer', company='Corp',
            description='Lead architecture', posted_by=self.user,
            requirements_text='Python, Django, Kubernetes, AWS, Microservices, System Design',
            level='senior', experience_years=5,
            tech_stack=['Python', 'Kubernetes', 'AWS'],
        )
        result = analyze_job(job)
        self.assertIn(result['detected_level'], ('mid', 'senior'))
        self.assertGreaterEqual(result['honesty_score'], 50)

    def test_analysis_saves_to_job(self):
        job = Job.objects.create(
            title='Mid Dev', company='Corp',
            description='d', posted_by=self.user,
            requirements_text='Python, Django, Docker, React',
            level='mid', tech_stack=[],
        )
        response = self.client.get(f'/api/analytics/analyze/{job.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        job.refresh_from_db()
        self.assertNotEqual(job.parsed_skills, [])
        self.assertNotEqual(job.detected_level, '')


# --- Unit tests: recommendation_engine ---


class RecommendationTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='dev', password='pass123')
        self.profile = UserProfile.objects.create(
            user=self.user, role='applicant', level='junior',
            skills=['Python', 'Django', 'HTML', 'CSS', 'Git', 'SQL'],
            verified_skills=['Python', 'Django', 'HTML', 'CSS', 'Git', 'SQL'],
        )
        self.hr = User.objects.create_user(username='hr', password='pass123')

    def test_high_match(self):
        job = Job.objects.create(
            title='Junior Python Dev', company='Corp',
            description='d', posted_by=self.hr,
            requirements_text='Python, Django, HTML, CSS, Git',
            level='junior', tech_stack=['Python', 'Django'],
        )
        result = generate_recommendation(self.profile, job)
        self.assertGreaterEqual(result['match_score'], 70)
        self.assertTrue(result['can_apply'])

    def test_low_match(self):
        job = Job.objects.create(
            title='React Developer', company='Corp',
            description='d', posted_by=self.hr,
            requirements_text='React, TypeScript, Next.js, GraphQL, Tailwind CSS',
            level='mid', tech_stack=['React', 'TypeScript'],
        )
        result = generate_recommendation(self.profile, job)
        self.assertLess(result['match_score'], 30)
        self.assertGreater(len(result['missing_skills']), 0)

    def test_calculate_match_empty_job(self):
        result = calculate_match(['Python', 'Django'], [])
        self.assertEqual(result['match_score'], 100)

    def test_calculate_match_no_overlap(self):
        result = calculate_match(['Python'], ['React', 'Vue'])
        self.assertEqual(result['match_score'], 0)
        self.assertEqual(result['missing_skills'], ['React', 'Vue'])

    def test_match_api_endpoint(self):
        self.client.force_authenticate(user=self.user)
        job = Job.objects.create(
            title='Test', company='Corp', description='d',
            requirements_text='Python, Django', level='junior',
            posted_by=self.hr, tech_stack=[],
        )
        response = self.client.post('/api/analytics/match/', {
            'job_id': job.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('match_score', response.data)
        self.assertIn('recommendation', response.data)


# --- Unit tests: comparison ---


class ComparisonTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='dev', password='pass123')
        self.profile = UserProfile.objects.create(
            user=self.user, role='applicant', level='junior',
            skills=['Python', 'Django', 'Git'],
        )
        self.hr = User.objects.create_user(username='hr', password='pass123')
        self.job1 = Job.objects.create(
            title='Python Dev', company='AlphaCorp',
            description='d', posted_by=self.hr,
            requirements_text='Python, Django, Git',
            level='junior', salary_min=200000, salary_max=400000,
            training_provided=True, tech_stack=['Python', 'Django'],
        )
        self.job2 = Job.objects.create(
            title='Go Engineer', company='BetaCorp',
            description='d', posted_by=self.hr,
            requirements_text='Go, Kubernetes, Docker, AWS',
            level='mid', salary_min=500000, salary_max=900000,
            tech_stack=['Go', 'Kubernetes'],
        )

    def test_compare_two_jobs(self):
        result = compare_jobs([self.job1, self.job2], self.profile)
        self.assertEqual(len(result['jobs']), 2)
        self.assertIn('comparison', result)
        self.assertIn('verdict', result)
        self.assertIn('winner_id', result['verdict'])

    def test_compare_without_user(self):
        result = compare_jobs([self.job1, self.job2])
        self.assertEqual(len(result['jobs']), 2)
        self.assertIsNone(result['jobs'][0]['match'])

    def test_compare_too_few_jobs(self):
        result = compare_jobs([self.job1])
        self.assertIn('error', result)

    def test_compare_api_endpoint(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/analytics/compare/', {
            'job_ids': [self.job1.id, self.job2.id],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['jobs']), 2)
        self.assertIn('verdict', response.data)


# --- Favorites API ---


class FavoriteAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='dev', password='pass123')
        self.hr = User.objects.create_user(username='hr', password='pass123')
        self.job = Job.objects.create(
            title='Test Job', company='Corp', description='d',
            requirements_text='r', posted_by=self.hr,
        )
        self.client.force_authenticate(user=self.user)

    def test_add_favorite(self):
        response = self.client.post('/api/analytics/favorites/', {
            'job_id': self.job.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Favorite.objects.count(), 1)

    def test_add_duplicate_favorite(self):
        Favorite.objects.create(user=self.user, job=self.job)
        response = self.client.post('/api/analytics/favorites/', {
            'job_id': self.job.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Favorite.objects.count(), 1)

    def test_list_favorites(self):
        Favorite.objects.create(user=self.user, job=self.job)
        response = self.client.get('/api/analytics/favorites/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_delete_favorite(self):
        fav = Favorite.objects.create(user=self.user, job=self.job)
        response = self.client.delete(f'/api/analytics/favorites/{fav.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Favorite.objects.count(), 0)
