from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from accounts.models import UserProfile
from jobs.models import Job
from .models import Application


class ApplicationModelTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='applicant', password='pass123')
        self.hr = User.objects.create_user(username='hr', password='pass123')
        self.job = Job.objects.create(
            title='Test Job', company='Corp', description='d',
            requirements_text='r', posted_by=self.hr,
        )

    def test_str_representation(self):
        app = Application.objects.create(applicant=self.user, job=self.job)
        self.assertEqual(str(app), 'applicant -> Test Job')

    def test_unique_together(self):
        Application.objects.create(applicant=self.user, job=self.job)
        with self.assertRaises(Exception):
            Application.objects.create(applicant=self.user, job=self.job)

    def test_default_status(self):
        app = Application.objects.create(applicant=self.user, job=self.job)
        self.assertEqual(app.status, 'pending')


class ApplicationAPITest(APITestCase):
    """Tests for /api/applications/ endpoints."""

    def setUp(self):
        self.applicant = User.objects.create_user(username='applicant', password='pass123')
        UserProfile.objects.create(user=self.applicant, role='applicant')
        self.hr = User.objects.create_user(username='hr', password='pass123')
        UserProfile.objects.create(user=self.hr, role='hr')
        self.job = Job.objects.create(
            title='Python Dev', company='Corp', description='d',
            requirements_text='Python', posted_by=self.hr,
        )

    def test_create_application(self):
        self.client.force_authenticate(user=self.applicant)
        data = {
            'job': self.job.id,
            'cover_letter': 'I am interested',
        }
        response = self.client.post('/api/applications/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Application.objects.count(), 1)

    def test_list_applications_as_applicant(self):
        self.client.force_authenticate(user=self.applicant)
        Application.objects.create(applicant=self.applicant, job=self.job)
        response = self.client.get('/api/applications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_list_applications_as_hr(self):
        self.client.force_authenticate(user=self.hr)
        Application.objects.create(applicant=self.applicant, job=self.job)
        response = self.client.get('/api/applications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_job(self):
        self.client.force_authenticate(user=self.hr)
        Application.objects.create(applicant=self.applicant, job=self.job)
        response = self.client.get(f'/api/applications/?job_id={self.job.id}')
        self.assertEqual(response.data['count'], 1)

    def test_application_detail(self):
        self.client.force_authenticate(user=self.applicant)
        app = Application.objects.create(
            applicant=self.applicant, job=self.job, cover_letter='Hello',
        )
        response = self.client.get(f'/api/applications/{app.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cover_letter'], 'Hello')

    def test_update_status_as_hr(self):
        self.client.force_authenticate(user=self.hr)
        app = Application.objects.create(applicant=self.applicant, job=self.job)
        response = self.client.patch(
            f'/api/applications/{app.id}/status/',
            {'status': 'accepted'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        app.refresh_from_db()
        self.assertEqual(app.status, 'accepted')

    def test_update_status_rejected(self):
        self.client.force_authenticate(user=self.hr)
        app = Application.objects.create(applicant=self.applicant, job=self.job)
        response = self.client.patch(
            f'/api/applications/{app.id}/status/',
            {'status': 'rejected'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        app.refresh_from_db()
        self.assertEqual(app.status, 'rejected')

    def test_unauthenticated_cannot_create(self):
        data = {'job': self.job.id, 'cover_letter': 'test'}
        response = self.client.post('/api/applications/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
