from rest_framework import serializers
from .models import Job, JobTag


class JobTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTag
        fields = ['id', 'name']


class JobListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view."""
    tags = JobTagSerializer(many=True, read_only=True)
    posted_by_username = serializers.CharField(source='posted_by.username', read_only=True)
    applications_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company', 'location', 'is_remote',
            'salary_min', 'salary_max', 'level',
            'training_provided', 'experience_years', 'tech_stack',
            'detected_level', 'is_overqualified', 'honesty_score',
            'posted_by_username', 'applications_count', 'tags',
            'created_at',
        ]


class JobDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail view."""
    tags = JobTagSerializer(many=True, read_only=True)
    posted_by_username = serializers.CharField(source='posted_by.username', read_only=True)
    applications_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'company', 'location', 'is_remote',
            'salary_min', 'salary_max', 'level', 'requirements_text',
            'training_provided', 'experience_years', 'tech_stack',
            'detected_level', 'is_overqualified', 'honesty_score', 'parsed_skills',
            'posted_by', 'posted_by_username', 'applications_count', 'tags',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'detected_level', 'is_overqualified', 'honesty_score', 'parsed_skills',
            'created_at', 'updated_at',
        ]


class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'company', 'location', 'is_remote',
            'salary_min', 'salary_max', 'level', 'requirements_text',
            'training_provided', 'experience_years', 'tech_stack',
        ]
