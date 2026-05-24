from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone
from .models import SkillTest, Question, TestResult, Answer, CodeSubmission
from .serializers import (
    SkillTestListSerializer,
    SkillTestDetailSerializer,
    QuestionDetailSerializer,
    TestResultSerializer,
    TestResultListSerializer,
    TestSubmitSerializer,
    CodeSubmitSerializer,
    CodeSubmissionSerializer,
)
from .code_runner import execute_code

LANGUAGE_TO_SKILL = {
    'python': 'Python',
    'javascript': 'JavaScript',
    'java': 'Java',
    'react': 'React',
}


def _verify_skill_for_user(user, test):
    skill_name = LANGUAGE_TO_SKILL.get(test.language)
    if not skill_name:
        return
    profile = getattr(user, 'profile', None)
    if not profile:
        return
    verified = profile.verified_skills or []
    if skill_name not in verified:
        verified.append(skill_name)
        profile.verified_skills = verified
        if skill_name not in (profile.skills or []):
            profile.skills = (profile.skills or []) + [skill_name]
        profile.save(update_fields=['verified_skills', 'skills'])


class SkillTestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

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
        test = self.get_object()
        submit_serializer = TestSubmitSerializer(data=request.data)
        submit_serializer.is_valid(raise_exception=True)

        user = request.user

        existing = TestResult.objects.filter(
            user=user, test=test, completed_at__isnull=False
        ).first()
        if existing:
            return Response(
                TestResultSerializer(existing).data,
                status=status.HTTP_200_OK,
            )

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

        if result.status == 'passed':
            _verify_skill_for_user(user, test)

        return Response(
            TestResultSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )


class TestResultViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TestResult.objects.select_related('test', 'user').filter(
            user=self.request.user
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return TestResultListSerializer
        return TestResultSerializer


class CodeChallengeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='submit/(?P<question_id>[^/.]+)')
    def submit_code(self, request, question_id=None):
        try:
            question = Question.objects.get(id=question_id, question_type='code')
        except Question.DoesNotExist:
            return Response(
                {'detail': 'Code challenge not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CodeSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_code = serializer.validated_data['code']

        if not question.test_code:
            return Response(
                {'detail': 'No tests configured for this challenge'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = execute_code(user_code, question.test_code)

        submission = CodeSubmission.objects.create(
            user=request.user,
            question=question,
            code=user_code,
            status=result['status'],
            output=result['output'],
            test_results=result['test_results'],
            tests_passed=result['tests_passed'],
            tests_total=result['tests_total'],
            execution_time_ms=result['execution_time_ms'],
            error_message=result['error_message'],
        )

        response_data = CodeSubmissionSerializer(submission).data

        if result['status'] == 'passed':
            self._update_test_result(request.user, question)

        return Response(response_data, status=status.HTTP_201_CREATED)

    def _update_test_result(self, user, question):
        test = question.test
        all_questions = test.questions.filter(question_type='code')
        total = all_questions.count()

        passed_questions = 0
        for q in all_questions:
            has_passed = CodeSubmission.objects.filter(
                user=user, question=q, status='passed'
            ).exists()
            if has_passed:
                passed_questions += 1

        score = passed_questions * 10
        max_score = total * 10
        test_status = 'passed' if passed_questions == total else 'failed'

        result, _ = TestResult.objects.update_or_create(
            user=user,
            test=test,
            defaults={
                'score': score,
                'max_score': max_score,
                'status': test_status,
                'completed_at': timezone.now() if test_status == 'passed' else None,
            },
        )

        if test_status == 'passed':
            _verify_skill_for_user(user, test)

    @action(detail=False, methods=['get'], url_path='history/(?P<question_id>[^/.]+)')
    def history(self, request, question_id=None):
        submissions = CodeSubmission.objects.filter(
            user=request.user,
            question_id=question_id,
        )[:10]
        return Response(
            CodeSubmissionSerializer(submissions, many=True).data,
        )

    @action(detail=False, methods=['get'], url_path='progress/(?P<test_id>[^/.]+)')
    def progress(self, request, test_id=None):
        try:
            test = SkillTest.objects.get(id=test_id)
        except SkillTest.DoesNotExist:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        questions = test.questions.filter(question_type='code')
        progress = []
        for q in questions:
            best = CodeSubmission.objects.filter(
                user=request.user, question=q
            ).order_by('-tests_passed').first()
            progress.append({
                'question_id': q.id,
                'question_text': q.text[:80],
                'order': q.order,
                'solved': best.status == 'passed' if best else False,
                'attempts': CodeSubmission.objects.filter(user=request.user, question=q).count(),
                'best_score': f"{best.tests_passed}/{best.tests_total}" if best else "0/0",
            })

        total_result = TestResult.objects.filter(user=request.user, test=test).first()
        return Response({
            'test_id': test.id,
            'test_title': test.title,
            'tasks': progress,
            'solved_count': sum(1 for p in progress if p['solved']),
            'total_count': len(progress),
            'completed': total_result.status == 'passed' if total_result else False,
        })
