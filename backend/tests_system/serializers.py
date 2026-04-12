from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import SkillTest, Question, TestResult, Answer


class QuestionListSerializer(serializers.ModelSerializer):
    """Question without correct answer — for test-taking."""
    class Meta:
        model = Question
        fields = [
            'id', 'question_type', 'text', 'order',
            'option_a', 'option_b', 'option_c', 'option_d',
            'code_template',
        ]


class QuestionDetailSerializer(serializers.ModelSerializer):
    """Full question with correct answer — for admin/review."""
    class Meta:
        model = Question
        fields = [
            'id', 'question_type', 'text', 'order',
            'option_a', 'option_b', 'option_c', 'option_d',
            'correct_answer', 'code_template', 'test_code',
            'created_at',
        ]


class SkillTestListSerializer(serializers.ModelSerializer):
    """Lightweight test listing."""
    questions_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = SkillTest
        fields = [
            'id', 'title', 'language', 'description',
            'difficulty', 'questions_count', 'created_at',
        ]


class SkillTestDetailSerializer(serializers.ModelSerializer):
    """Full test with nested questions (without answers)."""
    questions = QuestionListSerializer(many=True, read_only=True)

    class Meta:
        model = SkillTest
        fields = [
            'id', 'title', 'language', 'description',
            'difficulty', 'questions', 'created_at', 'updated_at',
        ]


class AnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    question_order = serializers.IntegerField(source='question.order', read_only=True)

    class Meta:
        model = Answer
        fields = [
            'id', 'question', 'question_text', 'question_order',
            'user_answer', 'is_correct',
        ]
        read_only_fields = ['is_correct']


class SubmitAnswerSerializer(serializers.Serializer):
    """For submitting answers during a test."""
    question_id = serializers.IntegerField()
    answer = serializers.CharField()


class TestSubmitSerializer(serializers.Serializer):
    """For submitting an entire test at once."""
    answers = SubmitAnswerSerializer(many=True)


class TestResultSerializer(serializers.ModelSerializer):
    """Test result with nested answers."""
    test_title = serializers.CharField(source='test.title', read_only=True)
    test_language = serializers.CharField(source='test.language', read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = TestResult
        fields = [
            'id', 'user', 'test', 'test_title', 'test_language',
            'score', 'max_score', 'percentage', 'status',
            'started_at', 'completed_at', 'duration_seconds',
            'answers',
        ]
        read_only_fields = [
            'score', 'max_score', 'status',
            'started_at', 'completed_at', 'duration_seconds',
        ]

    @extend_schema_field(serializers.IntegerField())
    def get_percentage(self, obj):
        if obj.max_score == 0:
            return 0
        return round((obj.score / obj.max_score) * 100)


class TestResultListSerializer(serializers.ModelSerializer):
    """Lightweight result for lists — no nested answers."""
    test_title = serializers.CharField(source='test.title', read_only=True)
    test_language = serializers.CharField(source='test.language', read_only=True)
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = TestResult
        fields = [
            'id', 'test', 'test_title', 'test_language',
            'score', 'max_score', 'percentage', 'status',
            'started_at', 'completed_at',
        ]

    @extend_schema_field(serializers.IntegerField())
    def get_percentage(self, obj):
        if obj.max_score == 0:
            return 0
        return round((obj.score / obj.max_score) * 100)
