from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import SkillTest, Question, TestResult, Answer


class SkillTestModelTest(APITestCase):

    def test_str_representation(self):
        test = SkillTest.objects.create(
            title='Python Basics', language='python',
            description='Test your Python skills', difficulty='easy',
        )
        self.assertEqual(str(test), 'Python Basics (python)')

    def test_question_str(self):
        test = SkillTest.objects.create(
            title='JS Quiz', language='javascript',
            description='d', difficulty='medium',
        )
        q = Question.objects.create(
            test=test, question_type='quiz', text='What is JS?', order=1,
        )
        self.assertEqual(str(q), 'JS Quiz - Q1')


class SkillTestAPITest(APITestCase):
    """Tests for /api/tests/ endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(username='student', password='pass123')
        self.test = SkillTest.objects.create(
            title='Python Basics',
            language='python',
            description='Test your Python fundamentals',
            difficulty='easy',
        )
        self.q1 = Question.objects.create(
            test=self.test, question_type='quiz',
            text='What is Python?', order=1,
            option_a='A language', option_b='A snake',
            option_c='A framework', option_d='A database',
            correct_answer='a',
        )
        self.q2 = Question.objects.create(
            test=self.test, question_type='quiz',
            text='What is PEP 8?', order=2,
            option_a='A library', option_b='A style guide',
            option_c='A package', option_d='An IDE',
            correct_answer='b',
        )

    def test_list_tests(self):
        response = self.client.get('/api/tests/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Python Basics')

    def test_list_includes_question_count(self):
        response = self.client.get('/api/tests/')
        self.assertEqual(response.data['results'][0]['questions_count'], 2)

    def test_detail_includes_questions(self):
        response = self.client.get(f'/api/tests/{self.test.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['questions']), 2)
        # Should NOT include correct_answer in questions
        self.assertNotIn('correct_answer', response.data['questions'][0])

    def test_submit_test_passing(self):
        data = {
            'user_id': self.user.id,
            'answers': [
                {'question_id': self.q1.id, 'answer': 'a'},
                {'question_id': self.q2.id, 'answer': 'b'},
            ],
        }
        response = self.client.post(
            f'/api/tests/{self.test.id}/submit/', data, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 20)
        self.assertEqual(response.data['max_score'], 20)
        self.assertEqual(response.data['status'], 'passed')

    def test_submit_test_failing(self):
        data = {
            'user_id': self.user.id,
            'answers': [
                {'question_id': self.q1.id, 'answer': 'c'},  # wrong
                {'question_id': self.q2.id, 'answer': 'c'},  # wrong
            ],
        }
        response = self.client.post(
            f'/api/tests/{self.test.id}/submit/', data, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 0)
        self.assertEqual(response.data['status'], 'failed')

    def test_submit_test_partial(self):
        data = {
            'user_id': self.user.id,
            'answers': [
                {'question_id': self.q1.id, 'answer': 'a'},  # correct
                {'question_id': self.q2.id, 'answer': 'c'},  # wrong
            ],
        }
        response = self.client.post(
            f'/api/tests/{self.test.id}/submit/', data, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 10)
        # 50% < 70% threshold → failed
        self.assertEqual(response.data['status'], 'failed')

    def test_submit_without_user_id(self):
        data = {
            'answers': [
                {'question_id': self.q1.id, 'answer': 'a'},
            ],
        }
        response = self.client.post(
            f'/api/tests/{self.test.id}/submit/', data, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_already_completed(self):
        """Submitting same test twice returns existing result."""
        data = {
            'user_id': self.user.id,
            'answers': [
                {'question_id': self.q1.id, 'answer': 'a'},
                {'question_id': self.q2.id, 'answer': 'b'},
            ],
        }
        self.client.post(f'/api/tests/{self.test.id}/submit/', data, format='json')
        response = self.client.post(
            f'/api/tests/{self.test.id}/submit/', data, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(TestResult.objects.filter(user=self.user, test=self.test).count(), 1)


class TestResultAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='student', password='pass123')
        self.test = SkillTest.objects.create(
            title='JS Quiz', language='javascript',
            description='d', difficulty='medium',
        )
        self.result = TestResult.objects.create(
            user=self.user, test=self.test,
            score=80, max_score=100, status='passed',
        )

    def test_list_results(self):
        response = self.client.get('/api/tests/results/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_user(self):
        other = User.objects.create_user(username='other', password='pass123')
        TestResult.objects.create(
            user=other, test=self.test, score=50, max_score=100,
        )
        response = self.client.get(f'/api/tests/results/?user_id={self.user.id}')
        self.assertEqual(response.data['count'], 1)

    def test_result_detail_has_percentage(self):
        response = self.client.get(f'/api/tests/results/{self.result.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['percentage'], 80)
