from rest_framework import serializers
from .models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_company = serializers.CharField(source='job.company', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'job', 'job_title', 'job_company', 'created_at']
        read_only_fields = ['created_at']


class FavoriteCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    job_id = serializers.IntegerField()


class AnalyzeJobSerializer(serializers.Serializer):
    """Response serializer for job analysis."""
    parsed_skills = serializers.ListField(child=serializers.CharField())
    skills_by_level = serializers.DictField()
    detected_level = serializers.CharField()
    is_overqualified = serializers.BooleanField()
    honesty_score = serializers.IntegerField()
    experience_from_text = serializers.IntegerField()
    overqualification_details = serializers.DictField()


class MatchRequestSerializer(serializers.Serializer):
    """Request for match calculation."""
    user_id = serializers.IntegerField()
    job_id = serializers.IntegerField()


class MatchResponseSerializer(serializers.Serializer):
    """Response serializer for match calculation."""
    match_score = serializers.IntegerField()
    can_apply = serializers.BooleanField()
    matching_skills = serializers.ListField(child=serializers.CharField())
    missing_skills = serializers.ListField(child=serializers.CharField())
    recommendation = serializers.CharField()
    learning_path = serializers.ListField(child=serializers.CharField())


class CompareRequestSerializer(serializers.Serializer):
    """Request for job comparison."""
    job_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=2,
        max_length=4,
    )
    user_id = serializers.IntegerField(required=False)
