from rest_framework import serializers
from .models import LiveSession, SessionResult
from tests_system.serializers import QuestionDetailSerializer


class LiveSessionCreateSerializer(serializers.ModelSerializer):
    question_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = LiveSession
        fields = ['title', 'time_limit_minutes', 'question_ids']

    def create(self, validated_data):
        question_ids = validated_data.pop('question_ids')
        session = LiveSession.objects.create(
            hr=self.context['request'].user,
            **validated_data
        )
        session.questions.set(question_ids)
        return session


class LiveSessionListSerializer(serializers.ModelSerializer):
    hr_username = serializers.CharField(source='hr.username', read_only=True)
    candidate_username = serializers.CharField(source='candidate.username', read_only=True, default=None)
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = LiveSession
        fields = [
            'id', 'title', 'status', 'invite_code', 'time_limit_minutes',
            'hr_username', 'candidate_username', 'questions_count',
            'started_at', 'completed_at', 'created_at',
        ]

    def get_questions_count(self, obj):
        return obj.questions.count()


class LiveSessionDetailSerializer(serializers.ModelSerializer):
    hr_username = serializers.CharField(source='hr.username', read_only=True)
    candidate_username = serializers.CharField(source='candidate.username', read_only=True, default=None)
    questions = QuestionDetailSerializer(many=True, read_only=True)
    results = serializers.SerializerMethodField()

    class Meta:
        model = LiveSession
        fields = [
            'id', 'title', 'status', 'invite_code', 'time_limit_minutes',
            'hr_username', 'candidate_username', 'questions',
            'candidate_code', 'current_question_index',
            'started_at', 'completed_at', 'created_at', 'results',
        ]

    def get_results(self, obj):
        return SessionResultSerializer(obj.results.all(), many=True).data


class SessionResultSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)

    class Meta:
        model = SessionResult
        fields = ['id', 'question', 'question_text', 'code', 'status', 'tests_passed', 'tests_total', 'submitted_at']
