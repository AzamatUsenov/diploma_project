from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import LiveSession, SessionResult
from .serializers import (
    LiveSessionCreateSerializer,
    LiveSessionListSerializer,
    LiveSessionDetailSerializer,
)
from tests_system.code_runner import execute_code
from tests_system.models import Question
from applications.models import Application, Message


class LiveSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        profile = getattr(user, 'profile', None)
        if profile and profile.role == 'hr':
            return LiveSession.objects.filter(hr=user)
        return LiveSession.objects.filter(candidate=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return LiveSessionCreateSerializer
        if self.action == 'list':
            return LiveSessionListSerializer
        return LiveSessionDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.save()
        return Response(
            LiveSessionDetailSerializer(session).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['post'], url_path='join')
    def join(self, request):
        code = request.data.get('invite_code', '').strip().upper()
        session = get_object_or_404(LiveSession, invite_code=code, status='waiting')
        session.candidate = request.user
        session.status = 'active'
        session.started_at = timezone.now()
        session.save()
        return Response(LiveSessionDetailSerializer(session).data)

    @action(detail=True, methods=['post'], url_path='submit-task')
    def submit_task(self, request, pk=None):
        session = self.get_object()
        if session.status != 'active':
            return Response({'detail': 'Session is not active'}, status=status.HTTP_400_BAD_REQUEST)

        code = request.data.get('code', '')
        question_id = request.data.get('question_id')

        question = session.questions.filter(id=question_id).first()
        if not question:
            return Response({'detail': 'Question not in session'}, status=status.HTTP_400_BAD_REQUEST)

        result = execute_code(code, question.test_code)

        SessionResult.objects.create(
            session=session,
            question=question,
            code=code,
            status=result['status'],
            tests_passed=result['tests_passed'],
            tests_total=result['tests_total'],
        )

        return Response({
            'status': result['status'],
            'output': result['output'],
            'tests_passed': result['tests_passed'],
            'tests_total': result['tests_total'],
            'test_results': result['test_results'],
        })

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        session = self.get_object()
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.save()
        return Response(LiveSessionDetailSerializer(session).data)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        session = self.get_object()
        session.status = 'cancelled'
        session.save()
        return Response({'status': 'cancelled'})

    @action(detail=True, methods=['post'], url_path='extend-time')
    def extend_time(self, request, pk=None):
        session = self.get_object()
        if session.hr != request.user:
            return Response({'detail': 'Only HR can extend time'}, status=status.HTTP_403_FORBIDDEN)
        if session.status not in ('waiting', 'active'):
            return Response({'detail': 'Cannot extend completed session'}, status=status.HTTP_400_BAD_REQUEST)

        extra_minutes = request.data.get('minutes', 15)
        try:
            extra_minutes = int(extra_minutes)
        except (TypeError, ValueError):
            return Response({'detail': 'Invalid minutes'}, status=status.HTTP_400_BAD_REQUEST)

        if extra_minutes < 5 or extra_minutes > 60:
            return Response({'detail': 'Minutes must be between 5 and 60'}, status=status.HTTP_400_BAD_REQUEST)

        session.time_limit_minutes += extra_minutes
        session.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'live_session_{session.id}',
            {
                'type': 'extend_time_broadcast',
                'added': extra_minutes,
                'total_minutes': session.time_limit_minutes,
            }
        )

        return Response({
            'time_limit_minutes': session.time_limit_minutes,
            'added': extra_minutes,
        })

    @action(detail=True, methods=['post'], url_path='send-invite')
    def send_invite(self, request, pk=None):
        session = self.get_object()
        application_id = request.data.get('application_id')
        if not application_id:
            return Response({'detail': 'application_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        application = get_object_or_404(Application, id=application_id)

        if application.job.posted_by != request.user:
            return Response({'detail': 'Not your application'}, status=status.HTTP_403_FORBIDDEN)

        invite_url = f"/live/?code={session.invite_code}"
        text = (
            f"Приглашаю вас на Live Coding сессию!\n\n"
            f"Название: {session.title}\n"
            f"Время: {session.time_limit_minutes} мин\n"
            f"Код приглашения: {session.invite_code}\n\n"
            f"Перейдите по ссылке: {invite_url}"
        )

        Message.objects.create(
            application=application,
            sender=request.user,
            text=text,
        )

        return Response({
            'status': 'sent',
            'invite_code': session.invite_code,
            'message': text,
        })

    @action(detail=False, methods=['get'], url_path='available-tasks')
    def available_tasks(self, request):
        questions = Question.objects.filter(question_type='code').select_related('test')
        tasks = [
            {
                'id': q.id,
                'text': q.text,
                'test_title': q.test.title,
                'language': q.test.language,
                'order': q.order,
            }
            for q in questions
        ]
        return Response(tasks)
