from rest_framework import serializers
from .models import CompanyReview


class CompanyReviewSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = CompanyReview
        fields = [
            'id', 'company_name', 'author_name', 'is_anonymous',
            'rating_overall', 'rating_work_life', 'rating_career_growth',
            'rating_salary', 'rating_management', 'average_rating',
            'title', 'pros', 'cons', 'advice',
            'is_current_employee', 'position',
            'helpful_count', 'created_at',
        ]
        read_only_fields = ['id', 'helpful_count', 'created_at']

    def get_author_name(self, obj):
        if obj.is_anonymous:
            return 'Аноним'
        return obj.author.username

    def validate(self, attrs):
        rating_fields = [
            'rating_overall', 'rating_work_life', 'rating_career_growth',
            'rating_salary', 'rating_management',
        ]
        for field in rating_fields:
            val = attrs.get(field)
            if val is not None and not (1 <= val <= 5):
                raise serializers.ValidationError({field: 'Рейтинг должен быть от 1 до 5'})
        return attrs


class CompanyStatsSerializer(serializers.Serializer):
    company_name = serializers.CharField()
    review_count = serializers.IntegerField()
    avg_overall = serializers.FloatField()
    avg_work_life = serializers.FloatField()
    avg_career_growth = serializers.FloatField()
    avg_salary = serializers.FloatField()
    avg_management = serializers.FloatField()
    avg_total = serializers.FloatField()
