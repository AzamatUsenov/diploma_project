from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import UserProfile
from .models import CompanyReview, ReviewHelpful


class ReviewModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass1234')
        self.review = CompanyReview.objects.create(
            company_name='TestCorp',
            author=self.user,
            rating_overall=4,
            rating_work_life=5,
            rating_career_growth=3,
            rating_salary=4,
            rating_management=4,
            title='Great place',
            pros='Good culture',
            cons='Low salary',
        )

    def test_str(self):
        self.assertIn('TestCorp', str(self.review))

    def test_average_rating(self):
        expected = round((4 + 5 + 3 + 4 + 4) / 5, 1)
        self.assertEqual(self.review.average_rating, expected)

    def test_unique_together(self):
        with self.assertRaises(Exception):
            CompanyReview.objects.create(
                company_name='TestCorp',
                author=self.user,
                rating_overall=3, rating_work_life=3, rating_career_growth=3,
                rating_salary=3, rating_management=3,
                title='Dup', pros='X', cons='Y',
            )


class ReviewAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('reviewer', 'r@r.com', 'pass1234')
        self.other = User.objects.create_user('other', 'o@o.com', 'pass1234')
        UserProfile.objects.create(user=self.user, role='applicant')
        UserProfile.objects.create(user=self.other, role='applicant')

    def _auth(self, user=None):
        self.client.force_authenticate(user=user or self.user)

    def _create_review(self, company='TestCorp', user=None):
        self._auth(user)
        return self.client.post('/api/reviews/', {
            'company_name': company,
            'title': 'Good place',
            'pros': 'Nice people',
            'cons': 'Low pay',
            'rating_overall': 4,
            'rating_work_life': 5,
            'rating_career_growth': 3,
            'rating_salary': 3,
            'rating_management': 4,
            'is_anonymous': False,
            'is_current_employee': True,
            'position': 'Developer',
        }, format='json')

    def test_create_review(self):
        res = self._create_review()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['company_name'], 'TestCorp')
        self.assertEqual(res.data['author_name'], 'reviewer')

    def test_create_anonymous_review(self):
        self._auth()
        res = self.client.post('/api/reviews/', {
            'company_name': 'AnonCorp',
            'title': 'Hidden', 'pros': 'X', 'cons': 'Y',
            'rating_overall': 3, 'rating_work_life': 3,
            'rating_career_growth': 3, 'rating_salary': 3, 'rating_management': 3,
            'is_anonymous': True,
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['author_name'], 'Аноним')

    def test_list_reviews(self):
        self._create_review()
        self.client.force_authenticate(user=None)
        res = self.client.get('/api/reviews/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_by_company(self):
        self._create_review('Alpha')
        self._create_review('Beta', user=self.other)
        self.client.force_authenticate(user=None)
        res = self.client.get('/api/reviews/', {'company': 'Alpha'})
        data = res.data.get('results', res.data)
        self.assertTrue(all(r['company_name'] == 'Alpha' for r in data))

    def test_cannot_edit_others_review(self):
        self._create_review()
        review_id = CompanyReview.objects.first().id
        self._auth(self.other)
        res = self.client.patch(f'/api/reviews/{review_id}/', {'title': 'Hacked'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_others_review(self):
        self._create_review()
        review_id = CompanyReview.objects.first().id
        self._auth(self.other)
        res = self.client.delete(f'/api/reviews/{review_id}/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_my_reviews(self):
        self._create_review()
        self._auth()
        res = self.client.get('/api/reviews/my/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_company_stats(self):
        self._create_review('StatsCorp')
        self._create_review('StatsCorp', user=self.other)
        res = self.client.get('/api/reviews/company-stats/', {'company': 'StatsCorp'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['review_count'], 2)
        self.assertGreater(res.data['avg_overall'], 0)

    def test_company_stats_no_reviews(self):
        res = self.client.get('/api/reviews/company-stats/', {'company': 'Nobody'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['review_count'], 0)

    def test_company_stats_missing_param(self):
        res = self.client.get('/api/reviews/company-stats/')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_toggle_helpful(self):
        self._create_review()
        review_id = CompanyReview.objects.first().id
        self._auth(self.other)
        res = self.client.post(f'/api/reviews/{review_id}/helpful/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['helpful'])
        self.assertEqual(res.data['helpful_count'], 1)

        res = self.client.post(f'/api/reviews/{review_id}/helpful/')
        self.assertFalse(res.data['helpful'])
        self.assertEqual(res.data['helpful_count'], 0)

    def test_top_companies(self):
        self._create_review('TopCorp')
        res = self.client.get('/api/reviews/top-companies/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cannot_create(self):
        self.client.force_authenticate(user=None)
        res = self.client.post('/api/reviews/', {
            'company_name': 'X', 'title': 'X', 'pros': 'X', 'cons': 'X',
            'rating_overall': 3, 'rating_work_life': 3,
            'rating_career_growth': 3, 'rating_salary': 3, 'rating_management': 3,
        }, format='json')
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
