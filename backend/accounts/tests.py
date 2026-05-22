from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import UserProfile


class RegisterAPITest(APITestCase):
    """Tests for POST /api/accounts/register/"""

    def test_register_applicant(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'secret123',
            'role': 'applicant',
            'level': 'junior',
        }
        response = self.client.post('/api/accounts/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        profile = UserProfile.objects.get(user__username='newuser')
        self.assertEqual(profile.role, 'applicant')
        self.assertEqual(profile.level, 'junior')

    def test_register_hr(self):
        data = {
            'username': 'hruser',
            'email': 'hr@example.com',
            'password': 'secret123',
            'role': 'hr',
        }
        response = self.client.post('/api/accounts/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        profile = UserProfile.objects.get(user__username='hruser')
        self.assertEqual(profile.role, 'hr')

    def test_register_duplicate_username(self):
        User.objects.create_user(username='taken', password='pass123')
        data = {
            'username': 'taken',
            'email': 'new@example.com',
            'password': 'secret123',
        }
        response = self.client.post('/api/accounts/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        response = self.client.post('/api/accounts/register/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_short_password(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': '123',
        }
        response = self.client.post('/api/accounts/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileAPITest(APITestCase):
    """Tests for /api/accounts/profiles/"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.profile = UserProfile.objects.create(
            user=self.user, role='applicant', level='junior',
            skills=['Python', 'Django'],
        )
        self.client.force_authenticate(user=self.user)

    def test_list_profiles(self):
        response = self.client.get('/api/accounts/profiles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_get_profile_detail(self):
        response = self.client.get(f'/api/accounts/profiles/{self.profile.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['role'], 'applicant')
        self.assertEqual(response.data['level'], 'junior')
        self.assertEqual(response.data['skills'], ['Python', 'Django'])

    def test_update_profile(self):
        response = self.client.patch(
            f'/api/accounts/profiles/{self.profile.id}/',
            {'bio': 'Hello world', 'level': 'mid'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Hello world')
        self.assertEqual(self.profile.level, 'mid')

    def test_get_nonexistent_profile(self):
        response = self.client.get('/api/accounts/profiles/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_me_endpoint(self):
        response = self.client.get('/api/accounts/profiles/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_me_patch(self):
        response = self.client.patch(
            '/api/accounts/profiles/me/',
            {'bio': 'Updated bio'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Updated bio')


class UserProfileModelTest(APITestCase):
    """Tests for UserProfile model."""

    def test_str_representation(self):
        user = User.objects.create_user(username='john', password='pass123')
        profile = UserProfile.objects.create(user=user, role='applicant')
        self.assertEqual(str(profile), 'john (applicant)')

    def test_default_values(self):
        user = User.objects.create_user(username='jane', password='pass123')
        profile = UserProfile.objects.create(user=user)
        self.assertEqual(profile.role, 'applicant')
        self.assertEqual(profile.level, 'junior')
        self.assertEqual(profile.skills, [])
        self.assertEqual(profile.bio, '')
