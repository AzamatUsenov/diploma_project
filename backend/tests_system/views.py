from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from .models import SkillTest, Question, TestResult, Answer
from .serializers import (
    SkillTestListSerializer,
    SkillTestDetailSerializer,
    QuestionDetailSerializer,
    TestResultSerializer,
    TestResultListSerializer,
    TestSubmitSerializer,
)


class SkillTestViewSet(viewsets.ModelViewSet):
    """
    Skill tests management.
    list:     GET /api/tests/          (lightweight with question count)
    retrieve: GET /api/tests/{id}/     (full with nested questions)
    submit:   POST /api/tests/{id}/submit/  (submit answers)
    """
    permission_classes = [AllowAny]

    def get_queryset(self):
        return SkillTest.objects.annotate(
            questions_count=Count('questions')
        ).all()

    def get_serializer_class(self):
        if self.action == 'list':
            return SkillTestListSerializer
        return SkillTestDetailSerializer

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        """
        Submit test answers.
        POST /api/tests/{id}/submit/
        Body: { "user_id": 1, "answers": [{"question_id": 1, "answer": "a"}, ...] }
        """
        test = self.get_object()
        submit_serializer = TestSubmitSerializer(data=request.data)
        submit_serializer.is_valid(raise_exception=True)

        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.get(pk=user_id)

        # Check if already completed
        existing = TestResult.objects.filter(
            user=user, test=test, completed_at__isnull=False
        ).first()
        if existing:
            return Response(
                TestResultSerializer(existing).data,
                status=status.HTTP_200_OK,
            )

        # Create result
        result = TestResult.objects.create(user=user, test=test)

        score = 0
        questions = test.questions.all()
        answers_data = submit_serializer.validated_data['answers']

        question_map = {q.id: q for q in questions}

        for ans in answers_data:
            question = question_map.get(ans['question_id'])
            if not question:
                continue

            answer = Answer.objects.create(
                result=result,
                question=question,
                user_answer=ans['answer'],
            )

            if question.question_type == 'quiz' and ans['answer'] == question.correct_answer:
                answer.is_correct = True
                answer.save()
                score += 10

        total_questions = questions.count()
        result.score = score
        result.max_score = total_questions * 10
        result.status = 'passed' if total_questions > 0 and score >= (result.max_score * 0.7) else 'failed'
        result.completed_at = timezone.now()
        result.save()

        return Response(
            TestResultSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )


class TestResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View test results.
    list:     GET /api/tests/results/           (all results)
    retrieve: GET /api/tests/results/{id}/      (single result with answers)

    Query params:
      ?user_id=1  — filter by user
    """
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = TestResult.objects.select_related('test', 'user').all()

        user_id = self.request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return TestResultListSerializer
        return TestResultSerializer
