from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import SkillTest, Question, TestResult, Answer, CodeSubmission


class QuestionListSerializer(serializers.ModelSerializer):
    """Question without correct answer — for test-taking."""
    visible_tests = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'question_type', 'text', 'order',
            'option_a', 'option_b', 'option_c', 'option_d',
            'code_template', 'visible_tests',
        ]

    def get_visible_tests(self, obj):
        if obj.question_type != 'code' or not obj.test_code:
            return None
        lines = obj.test_code.strip().split('\n')
        test_names = []
        for line in lines:
            if '_run_test(' in line:
                start = line.find("'") + 1
                end = line.find("'", start)
                if start > 0 and end > start:
                    test_names.append(line[start:end])
                else:
                    start = line.find('"') + 1
                    end = line.find('"', start)
                    if start > 0 and end > start:
                        test_names.append(line[start:end])
        return test_names if test_names else None


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
    test_type = serializers.SerializerMethodField()

    class Meta:
        model = SkillTest
        fields = [
            'id', 'title', 'language', 'description',
            'difficulty', 'questions_count', 'test_type', 'created_at',
        ]

    def get_test_type(self, obj):
        if obj.questions.filter(question_type='code').exists():
            return 'code'
        return 'quiz'


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


class CodeSubmitSerializer(serializers.Serializer):
    code = serializers.CharField()


class CodeTestResultItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    passed = serializers.BooleanField()
    message = serializers.CharField()


class CodeSubmissionSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    test_results = CodeTestResultItemSerializer(many=True, read_only=True)

    class Meta:
        model = CodeSubmission
        fields = [
            'id', 'question', 'question_text', 'code', 'status',
            'output', 'test_results', 'tests_passed', 'tests_total',
            'execution_time_ms', 'error_message', 'created_at',
        ]
        read_only_fields = [
            'status', 'output', 'test_results', 'tests_passed',
            'tests_total', 'execution_time_ms', 'error_message',
        ]
