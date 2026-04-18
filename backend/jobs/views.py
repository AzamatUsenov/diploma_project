from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Count
from .models import Job, JobTag
from .serializers import (
    JobListSerializer,
    JobDetailSerializer,
    JobCreateSerializer,
    JobTagSerializer,
)
from accounts.permissions import IsHR, IsOwnerOrReadOnly, ReadOnly


class JobViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'company', 'location']
    ordering_fields = [
        'salary_min', 'salary_max', 'honesty_score',
        'created_at', 'title', 'company', 'experience_years',
    ]
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsHR(), IsOwnerOrReadOnly()]
        return [ReadOnly()]

    def get_queryset(self):
        qs = Job.objects.filter(is_active=True).annotate(
            applications_count=Count('applications')
        ).select_related('posted_by')

        level = self.request.query_params.get('level')
        if level:
            qs = qs.filter(level=level)

        is_remote = self.request.query_params.get('is_remote')
        if is_remote is not None:
            qs = qs.filter(is_remote=is_remote.lower() in ('true', '1'))

        training = self.request.query_params.get('training_provided')
        if training is not None:
            qs = qs.filter(training_provided=training.lower() in ('true', '1'))

        salary_min = self.request.query_params.get('salary_min')
        if salary_min:
            qs = qs.filter(salary_max__gte=int(salary_min))

        salary_max = self.request.query_params.get('salary_max')
        if salary_max:
            qs = qs.filter(salary_min__lte=int(salary_max))

        tech = self.request.query_params.get('tech')
        if tech:
            qs = qs.filter(tech_stack__contains=[tech])

        min_honesty = self.request.query_params.get('min_honesty')
        if min_honesty:
            qs = qs.filter(honesty_score__gte=int(min_honesty))

        is_overqualified = self.request.query_params.get('is_overqualified')
        if is_overqualified is not None:
            qs = qs.filter(is_overqualified=is_overqualified.lower() in ('true', '1'))

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        if self.action == 'create':
            return JobCreateSerializer
        return JobDetailSerializer

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class JobTagViewSet(viewsets.ModelViewSet):
    queryset = JobTag.objects.all()
    serializer_class = JobTagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
