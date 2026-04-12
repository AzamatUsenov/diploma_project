from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Application
from .serializers import (
    ApplicationListSerializer,
    ApplicationDetailSerializer,
    ApplicationCreateSerializer,
    ApplicationStatusSerializer,
)


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    Applications management.
    list:     GET /api/applications/
    retrieve: GET /api/applications/{id}/
    create:   POST /api/applications/         (body: job, cover_letter, applicant_id)
    status:   PATCH /api/applications/{id}/status/  (body: status)

    Query params:
      ?applicant_id=1   — filter by applicant
      ?job_id=1         — filter by job
    """
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Application.objects.select_related(
            'applicant', 'job'
        ).all()

        applicant_id = self.request.query_params.get('applicant_id')
        if applicant_id:
            qs = qs.filter(applicant_id=applicant_id)

        job_id = self.request.query_params.get('job_id')
        if job_id:
            qs = qs.filter(job_id=job_id)

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
        # Accept applicant_id from request body (no auth, MVP)
        applicant_id = self.request.data.get('applicant_id')
        if applicant_id:
            user = User.objects.get(pk=applicant_id)
            serializer.save(applicant=user)
        else:
            user = User.objects.first()
            serializer.save(applicant=user)

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        """HR updates application status: PATCH /api/applications/{id}/status/"""
        application = self.get_object()
        serializer = ApplicationStatusSerializer(
            application, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ApplicationDetailSerializer(application).data)
