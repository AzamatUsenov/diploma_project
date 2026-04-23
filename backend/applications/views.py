from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes as perm_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Application, Message
from .serializers import (
    ApplicationListSerializer,
    ApplicationDetailSerializer,
    ApplicationCreateSerializer,
    ApplicationStatusSerializer,
    MessageSerializer,
    MessageCreateSerializer,
)
from accounts.permissions import IsHR, IsApplicant


class ApplicationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Application.objects.select_related(
            'applicant', 'applicant__profile', 'job'
        ).all()
        user = self.request.user

        if hasattr(user, 'profile'):
            if user.profile.role == 'applicant':
                qs = qs.filter(applicant=user)
            elif user.profile.role == 'hr':
                qs = qs.filter(job__posted_by=user)

        job_id = self.request.query_params.get('job_id')
        if job_id:
            qs = qs.filter(job_id=job_id)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ApplicationListSerializer
        if self.action == 'create':
            return ApplicationCreateSerializer
        if self.action == 'update_status':
            return ApplicationStatusSerializer
        return ApplicationDetailSerializer

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        application = self.get_object()
        if not (hasattr(request.user, 'profile') and request.user.profile.role == 'hr'):
            return Response(
                {'detail': 'Only HR can update application status.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ApplicationStatusSerializer(
            application, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ApplicationDetailSerializer(application).data)

    # ---- Chat ----

    @action(detail=True, methods=['get'], url_path='messages')
    def messages(self, request, pk=None):
        application = self.get_object()
        msgs = application.messages.select_related('sender', 'sender__profile').all()
        application.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)
        return Response(MessageSerializer(msgs, many=True).data)

    @action(detail=True, methods=['post'], url_path='send')
    def send_message(self, request, pk=None):
        application = self.get_object()
        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        msg = Message.objects.create(
            application=application,
            sender=request.user,
            text=serializer.validated_data['text'],
        )
        return Response(MessageSerializer(msg).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='unread-count')
    def unread_count(self, request, pk=None):
        application = self.get_object()
        count = application.messages.exclude(sender=request.user).filter(is_read=False).count()
        return Response({'unread': count})


@api_view(['GET'])
@perm_classes([IsAuthenticated])
def hr_stats_view(request):
    user = request.user
    if not hasattr(user, 'profile') or user.profile.role != 'hr':
        return Response({'detail': 'HR only'}, status=status.HTTP_403_FORBIDDEN)

    apps = Application.objects.filter(job__posted_by=user)
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    total = apps.count()
    by_status = dict(apps.values_list('status').annotate(c=Count('id')).values_list('status', 'c'))
    new_this_week = apps.filter(created_at__gte=week_ago).count()
    new_this_month = apps.filter(created_at__gte=month_ago).count()

    from jobs.models import Job
    my_jobs = Job.objects.filter(posted_by=user, is_active=True)
    jobs_count = my_jobs.count()
    avg_honesty = my_jobs.aggregate(avg=Avg('honesty_score'))['avg'] or 0

    per_job = list(
        apps.values('job__id', 'job__title')
        .annotate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            accepted=Count('id', filter=Q(status='accepted')),
            rejected=Count('id', filter=Q(status='rejected')),
        )
        .order_by('-total')[:10]
    )

    unread_messages = Message.objects.filter(
        application__job__posted_by=user,
        is_read=False,
    ).exclude(sender=user).count()

    funnel = {
        'total': total,
        'pending': by_status.get('pending', 0),
        'reviewed': by_status.get('reviewed', 0) + by_status.get('viewed', 0),
        'accepted': by_status.get('accepted', 0),
        'rejected': by_status.get('rejected', 0),
    }
    if total > 0:
        funnel['acceptance_rate'] = round(funnel['accepted'] / total * 100)
        funnel['rejection_rate'] = round(funnel['rejected'] / total * 100)
    else:
        funnel['acceptance_rate'] = 0
        funnel['rejection_rate'] = 0

    return Response({
        'total_applications': total,
        'new_this_week': new_this_week,
        'new_this_month': new_this_month,
        'active_jobs': jobs_count,
        'avg_honesty': round(avg_honesty),
        'unread_messages': unread_messages,
        'funnel': funnel,
        'per_job': per_job,
    })
