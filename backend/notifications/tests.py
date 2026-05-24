from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from accounts.models import UserProfile
from jobs.models import Job
from applications.models import Application, Message
from tests_system.models import SkillTest, Question, TestResult
from .models import Notification


class NotificationModelTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')

    def test_str_representation(self):
        notif = Notification.objects.create(
            user=self.user,
            notification_type='new_message',
            title='Test notification',
            message='Body text',
        )
        self.assertEqual(str(notif), 'testuser: Test notification')

    def test_time_ago_just_now(self):
        notif = Notification.objects.create(
            user=self.user,
            notification_type='test_result',
            title='Test',
            message='msg',
        )
        self.assertIn('только что', notif.time_ago)

    def test_default_ordering_newest_first(self):
        self.assertEqual(Notification._meta.ordering, ['-created_at'])

    def test_default_is_read_false(self):
        notif = Notification.objects.create(
            user=self.user,
            notification_type='new_message',
            title='Test',
            message='msg',
        )
        self.assertFalse(notif.is_read)


class NotificationAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.other = User.objects.create_user(username='other', password='pass123')
        self.client.force_authenticate(user=self.user)

        self.n1 = Notification.objects.create(
            user=self.user, notification_type='new_message',
            title='Msg 1', message='Hello',
        )
        self.n2 = Notification.objects.create(
            user=self.user, notification_type='application_status',
            title='Status update', message='Accepted',
        )
        Notification.objects.create(
            user=self.other, notification_type='new_message',
            title='Other user', message='Not visible',
        )

    def test_list_only_own_notifications(self):
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mark_read(self):
        self.assertFalse(self.n1.is_read)
        response = self.client.post(f'/api/notifications/{self.n1.id}/mark_read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.n1.refresh_from_db()
        self.assertTrue(self.n1.is_read)

    def test_mark_all_read(self):
        response = self.client.post('/api/notifications/mark_all_read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated'], 2)
        self.assertEqual(
            Notification.objects.filter(user=self.user, is_read=False).count(), 0
        )

    def test_unread_count(self):
        response = self.client.get('/api/notifications/unread_count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_unread_count_after_read(self):
        self.n1.is_read = True
        self.n1.save()
        response = self.client.get('/api/notifications/unread_count/')
        self.assertEqual(response.data['count'], 1)

    def test_cannot_mark_other_users_notification(self):
        other_notif = Notification.objects.filter(user=self.other).first()
        response = self.client.post(f'/api/notifications/{other_notif.id}/mark_read/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_notification_detail(self):
        response = self.client.get(f'/api/notifications/{self.n1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Msg 1')
        self.assertIn('time_ago', response.data)

    def test_notification_has_time_ago_field(self):
        response = self.client.get('/api/notifications/')
        result = response.data['results'][0]
        self.assertIn('time_ago', result)


class NotificationSignalTest(APITestCase):

    def setUp(self):
        self.hr_user = User.objects.create_user(username='hr', password='pass123')
        UserProfile.objects.create(user=self.hr_user, role='hr')
        self.applicant = User.objects.create_user(username='applicant', password='pass123')
        UserProfile.objects.create(user=self.applicant, role='applicant')
        self.job = Job.objects.create(
            title='Python Dev', description='desc', company='Corp',
            location='Almaty', level='junior', requirements_text='Python',
            posted_by=self.hr_user,
        )

    def test_application_creates_notification_for_hr(self):
        Application.objects.create(applicant=self.applicant, job=self.job)
        notif = Notification.objects.filter(
            user=self.hr_user, notification_type='new_application'
        ).first()
        self.assertIsNotNone(notif)
        self.assertIn('applicant', notif.message)
        self.assertIn('Python Dev', notif.message)

    def test_application_accepted_notifies_applicant(self):
        app = Application.objects.create(applicant=self.applicant, job=self.job)
        Notification.objects.all().delete()
        app.status = 'accepted'
        app.save()
        notif = Notification.objects.filter(
            user=self.applicant, notification_type='application_status'
        ).first()
        self.assertIsNotNone(notif)
        self.assertIn('принят', notif.message)

    def test_application_rejected_notifies_applicant(self):
        app = Application.objects.create(applicant=self.applicant, job=self.job)
        Notification.objects.all().delete()
        app.status = 'rejected'
        app.save()
        notif = Notification.objects.filter(
            user=self.applicant, notification_type='application_status'
        ).first()
        self.assertIsNotNone(notif)
        self.assertIn('отклонён', notif.message)

    def test_message_creates_notification_for_recipient(self):
        app = Application.objects.create(applicant=self.applicant, job=self.job)
        Notification.objects.all().delete()
        Message.objects.create(
            application=app, sender=self.applicant, text='Hello HR!',
        )
        notif = Notification.objects.filter(
            user=self.hr_user, notification_type='new_message'
        ).first()
        self.assertIsNotNone(notif)
        self.assertIn('Hello HR!', notif.message)

    def test_message_from_hr_notifies_applicant(self):
        app = Application.objects.create(applicant=self.applicant, job=self.job)
        Notification.objects.all().delete()
        Message.objects.create(
            application=app, sender=self.hr_user, text='Welcome aboard!',
        )
        notif = Notification.objects.filter(
            user=self.applicant, notification_type='new_message'
        ).first()
        self.assertIsNotNone(notif)

    def test_test_result_creates_notification(self):
        from django.utils import timezone
        test = SkillTest.objects.create(
            title='Python Quiz', language='python',
            description='d', difficulty='easy',
        )
        TestResult.objects.create(
            user=self.applicant, test=test,
            score=80, max_score=100, status='passed',
            completed_at=timezone.now(),
        )
        notif = Notification.objects.filter(
            user=self.applicant, notification_type='test_result'
        ).first()
        self.assertIsNotNone(notif)
        self.assertIn('пройден', notif.message)

    def test_incomplete_test_result_no_notification(self):
        test = SkillTest.objects.create(
            title='JS Quiz', language='javascript',
            description='d', difficulty='medium',
        )
        Notification.objects.all().delete()
        TestResult.objects.create(
            user=self.applicant, test=test,
            score=0, max_score=100, completed_at=None,
        )
        count = Notification.objects.filter(
            user=self.applicant, notification_type='test_result'
        ).count()
        self.assertEqual(count, 0)
