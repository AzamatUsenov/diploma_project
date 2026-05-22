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

    def test_answer_str(self):
        user = User.objects.create_user(username='u', password='p')
        test = SkillTest.objects.create(
            title='Test', language='python', description='d', difficulty='easy',
        )
        q = Question.objects.create(
            test=test, question_type='quiz', text='Q?', order=1,
        )
        result = TestResult.objects.create(user=user, test=test)
        answer = Answer.objects.create(result=result, question=q, user_answer='a')
        self.assertEqual(str(answer), 'u - Q1')

    def test_result_str(self):
        user = User.objects.create_user(username='u2', password='p')
        test = SkillTest.objects.create(
            title='Quiz', language='python', description='d', difficulty='easy',
        )
        result = TestResult.objects.create(
            user=user, test=test, score=80, max_score=100,
        )
        self.assertEqual(str(result), 'u2 - Quiz: 80/100')

    def test_question_ordering(self):
        test = SkillTest.objects.create(
            title='Test', language='python', description='d', difficulty='easy',
        )
        q3 = Question.objects.create(test=test, question_type='quiz', text='Q3', order=3)
        q1 = Question.objects.create(test=test, question_type='quiz', text='Q1', order=1)
        q2 = Question.objects.create(test=test, question_type='quiz', text='Q2', order=2)
        questions = list(test.questions.all())
        self.assertEqual(questions[0].order, 1)
        self.assertEqual(questions[1].order, 2)
        self.assertEqual(questions[2].order, 3)


class SkillTestAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='student', password='pass123')
        self.client.force_authenticate(user=self.user)
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

    def test_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/tests/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_includes_questions(self):
        response = self.client.get(f'/api/tests/{self.test.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['questions']), 2)
        self.assertNotIn('correct_answer', response.data['questions'][0])

    def test_detail_question_fields(self):
        response = self.client.get(f'/api/tests/{self.test.id}/')
        q = response.data['questions'][0]
        self.assertIn('option_a', q)
        self.assertIn('option_b', q)
        self.assertIn('option_c', q)
        self.assertIn('option_d', q)
        self.assertIn('text', q)

    def test_submit_test_passing(self):
        data = {
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
            'answers': [
                {'question_id': self.q1.id, 'answer': 'c'},
                {'question_id': self.q2.id, 'answer': 'c'},
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
            'answers': [
                {'question_id': self.q1.id, 'answer': 'a'},
                {'question_id': self.q2.id, 'answer': 'c'},
            ],
        }
        response = self.client.post(
            f'/api/tests/{self.test.id}/submit/', data, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 10)
        self.assertEqual(response.data['status'], 'failed')

    def test_submit_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {
            'answers': [
                {'question_id': self.q1.id, 'answer': 'a'},
            ],
        }
        response = self.client.post(
            f'/api/tests/{self.test.id}/submit/', data, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_submit_empty_answers(self):
        data = {'answers': []}
        response = self.client.post(
            f'/api/tests/{self.test.id}/submit/', data, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 0)

    def test_submit_already_completed(self):
        data = {
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
        self.assertEqual(
            TestResult.objects.filter(user=self.user, test=self.test).count(), 1
        )

    def test_submit_creates_answer_records(self):
        data = {
            'answers': [
                {'question_id': self.q1.id, 'answer': 'a'},
                {'question_id': self.q2.id, 'answer': 'c'},
            ],
        }
        self.client.post(f'/api/tests/{self.test.id}/submit/', data, format='json')
        result = TestResult.objects.get(user=self.user, test=self.test)
        answers = result.answers.all()
        self.assertEqual(answers.count(), 2)
        correct = answers.filter(is_correct=True)
        self.assertEqual(correct.count(), 1)

    def test_submit_invalid_question_id_ignored(self):
        data = {
            'answers': [
                {'question_id': 99999, 'answer': 'a'},
                {'question_id': self.q1.id, 'answer': 'a'},
            ],
        }
        response = self.client.post(
            f'/api/tests/{self.test.id}/submit/', data, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['score'], 10)


class TestResultAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='student', password='pass123')
        self.client.force_authenticate(user=self.user)
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

    def test_list_results_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/tests/results/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_own_results(self):
        other = User.objects.create_user(username='other', password='pass123')
        TestResult.objects.create(
            user=other, test=self.test, score=50, max_score=100,
        )
        response = self.client.get('/api/tests/results/')
        self.assertEqual(response.data['count'], 1)

    def test_result_detail_has_percentage(self):
        response = self.client.get(f'/api/tests/results/{self.result.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['percentage'], 80)

    def test_result_detail_has_test_title(self):
        response = self.client.get(f'/api/tests/results/{self.result.id}/')
        self.assertEqual(response.data['test_title'], 'JS Quiz')

    def test_result_zero_max_score_percentage(self):
        result = TestResult.objects.create(
            user=self.user, test=self.test,
            score=0, max_score=0,
        )
        response = self.client.get(f'/api/tests/results/{result.id}/')
        self.assertEqual(response.data['percentage'], 0)
