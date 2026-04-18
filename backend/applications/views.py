from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Application
from .serializers import (
    ApplicationListSerializer,
    ApplicationDetailSerializer,
    ApplicationCreateSerializer,
    ApplicationStatusSerializer,
)
from accounts.permissions import IsHR, IsApplicant


class ApplicationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Application.objects.select_related('applicant', 'job').all()
        user = self.request.user

        if hasattr(user, 'profile'):
            if user.profile.role == 'applicant':
                qs = qs.filter(applicant=user)
            elif user.profile.role == 'hr':
                qs = qs.filter(job__posted_by=user)

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
