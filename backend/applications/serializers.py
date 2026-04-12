from rest_framework import serializers
from .models import Application


class ApplicationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing applications."""
    applicant_username = serializers.CharField(source='applicant.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_company = serializers.CharField(source='job.company', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'applicant', 'applicant_username',
            'job', 'job_title', 'job_company',
            'status', 'created_at',
        ]
        read_only_fields = ['applicant', 'status', 'created_at']


class ApplicationDetailSerializer(serializers.ModelSerializer):
    """Full serializer with cover letter and timestamps."""
    applicant_username = serializers.CharField(source='applicant.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_company = serializers.CharField(source='job.company', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'applicant', 'applicant_username',
            'job', 'job_title', 'job_company',
            'cover_letter', 'status',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['applicant', 'created_at', 'updated_at']


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new applications."""
    class Meta:
        model = Application
        fields = ['job', 'cover_letter']


class ApplicationStatusSerializer(serializers.ModelSerializer):
    """Serializer for HR to update application status."""
    class Meta:
        model = Application
        fields = ['status']
