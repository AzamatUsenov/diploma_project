from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Job, JobTag


class JobModelTest(APITestCase):
    """Tests for Job model."""

    def setUp(self):
        self.user = User.objects.create_user(username='hr', password='pass123')

    def test_str_representation(self):
        job = Job.objects.create(
            title='Python Dev', company='TestCorp',
            description='Test', requirements_text='Python',
            posted_by=self.user,
        )
        self.assertEqual(str(job), 'Python Dev at TestCorp')

    def test_default_ordering(self):
        """Jobs are ordered by -created_at (newest first)."""
        job1 = Job.objects.create(
            title='First', company='A', description='d',
            requirements_text='r', posted_by=self.user,
        )
        job2 = Job.objects.create(
            title='Second', company='B', description='d',
            requirements_text='r', posted_by=self.user,
        )
        jobs = list(Job.objects.all())
        # Both created in same instant, so verify ordering meta is set
        self.assertEqual(Job._meta.ordering, ['-created_at'])
        self.assertEqual(len(jobs), 2)

    def test_default_values(self):
        job = Job.objects.create(
            title='Test', company='Corp', description='d',
            requirements_text='r', posted_by=self.user,
        )
        self.assertEqual(job.level, 'junior')
        self.assertFalse(job.is_remote)
        self.assertFalse(job.training_provided)
        self.assertEqual(job.experience_years, 0)
        self.assertEqual(job.honesty_score, 100)
        self.assertTrue(job.is_active)


class JobTagModelTest(APITestCase):

    def test_str_representation(self):
        tag = JobTag.objects.create(name='Python')
        self.assertEqual(str(tag), 'Python')


class JobAPITest(APITestCase):
    """Tests for /api/jobs/ endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(username='hr', password='pass123')
        self.job1 = Job.objects.create(
            title='Junior Python Developer',
            company='AlphaCorp',
            description='Entry level position',
            requirements_text='Python, HTML, CSS',
            location='Almaty',
            level='junior',
            salary_min=200000,
            salary_max=400000,
            is_remote=True,
            training_provided=True,
            experience_years=0,
            tech_stack=['Python', 'Django'],
            honesty_score=90,
            posted_by=self.user,
        )
        self.job2 = Job.objects.create(
            title='Senior Go Engineer',
            company='BetaCorp',
            description='Senior position',
            requirements_text='Go, Kubernetes, AWS',
            location='Astana',
            level='senior',
            salary_min=800000,
            salary_max=1500000,
            is_remote=False,
            experience_years=5,
            tech_stack=['Go', 'Kubernetes'],
            honesty_score=70,
            posted_by=self.user,
        )

    def test_list_jobs(self):
        response = self.client.get('/api/jobs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_get_job_detail(self):
        response = self.client.get(f'/api/jobs/{self.job1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Junior Python Developer')
        self.assertEqual(response.data['company'], 'AlphaCorp')
        self.assertIn('description', response.data)  # detail has description

    def test_list_excludes_description(self):
        response = self.client.get('/api/jobs/')
        first_job = response.data['results'][0]
        self.assertNotIn('description', first_job)  # list is lightweight

    def test_create_job(self):
        data = {
            'title': 'New Job',
            'description': 'New job description',
            'company': 'NewCorp',
            'location': 'Remote',
            'requirements_text': 'Python, Django',
            'level': 'mid',
            'posted_by': self.user.id,
        }
        response = self.client.post('/api/jobs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Job.objects.count(), 3)

    def test_filter_by_level(self):
        response = self.client.get('/api/jobs/?level=junior')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Junior Python Developer')

    def test_filter_by_remote(self):
        response = self.client.get('/api/jobs/?is_remote=true')
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_training(self):
        response = self.client.get('/api/jobs/?training_provided=true')
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_salary_min(self):
        response = self.client.get('/api/jobs/?salary_min=500000')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['company'], 'BetaCorp')

    def test_filter_by_min_honesty(self):
        response = self.client.get('/api/jobs/?min_honesty=80')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['honesty_score'], 90)

    def test_search_by_title(self):
        response = self.client.get('/api/jobs/?search=Python')
        self.assertEqual(response.data['count'], 1)

    def test_search_by_company(self):
        response = self.client.get('/api/jobs/?search=BetaCorp')
        self.assertEqual(response.data['count'], 1)

    def test_ordering_by_salary(self):
        response = self.client.get('/api/jobs/?ordering=-salary_max')
        results = response.data['results']
        self.assertEqual(results[0]['company'], 'BetaCorp')  # higher salary first

    def test_inactive_jobs_excluded(self):
        self.job1.is_active = False
        self.job1.save()
        response = self.client.get('/api/jobs/')
        self.assertEqual(response.data['count'], 1)

    def test_get_nonexistent_job(self):
        response = self.client.get('/api/jobs/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class JobTagAPITest(APITestCase):

    def test_list_tags(self):
        JobTag.objects.create(name='Python')
        JobTag.objects.create(name='Django')
        response = self.client.get('/api/jobs/tags/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_tag(self):
        response = self.client.post('/api/jobs/tags/', {'name': 'React'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
