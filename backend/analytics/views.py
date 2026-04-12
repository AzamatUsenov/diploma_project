from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from jobs.models import Job
from accounts.models import UserProfile
from .models import Favorite
from .serializers import (
    FavoriteSerializer,
    FavoriteCreateSerializer,
    AnalyzeJobSerializer,
    MatchRequestSerializer,
    MatchResponseSerializer,
    CompareRequestSerializer,
)
from .job_analyzer import analyze_job
from .recommendation_engine import generate_recommendation
from .comparison import compare_jobs


class FavoriteViewSet(viewsets.ModelViewSet):
    """
    Favorites (wishlist) management.
    list:     GET /api/analytics/favorites/?user_id=1
    create:   POST /api/analytics/favorites/   (body: user_id, job_id)
    delete:   DELETE /api/analytics/favorites/{id}/
    """
    serializer_class = FavoriteSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Favorite.objects.select_related('job', 'user').all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs

    def create(self, request):
        serializer = FavoriteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, pk=serializer.validated_data['user_id'])
        job = get_object_or_404(Job, pk=serializer.validated_data['job_id'])

        favorite, created = Favorite.objects.get_or_create(user=user, job=job)
        if not created:
            return Response(
                {'detail': 'Already in favorites'},
                status=status.HTTP_200_OK,
            )
        return Response(
            FavoriteSerializer(favorite).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    summary='Анализ вакансии',
    description='Анализирует требования вакансии: определяет реальный уровень, '
                'честность требований, завышенность, извлекает навыки.',
    responses={200: AnalyzeJobSerializer},
    tags=['analytics'],
)
@api_view(['GET'])
def analyze_job_view(request, job_id):
    """
    Analyze a single job posting.
    GET /api/analytics/analyze/{job_id}/

    Returns parsed skills, detected level, honesty score, overqualification details.
    Also saves analysis results back to the Job model.
    """
    job = get_object_or_404(Job, pk=job_id)
    analysis = analyze_job(job)

    # Save results to job
    job.parsed_skills = analysis['parsed_skills']
    job.detected_level = analysis['detected_level']
    job.is_overqualified = analysis['is_overqualified']
    job.honesty_score = analysis['honesty_score']
    job.save(update_fields=['parsed_skills', 'detected_level', 'is_overqualified', 'honesty_score'])

    return Response(analysis)


@extend_schema(
    summary='Матчинг пользователя и вакансии',
    description='Рассчитывает процент совпадения навыков пользователя с требованиями вакансии. '
                'Возвращает совпадающие/недостающие навыки, рекомендации и план обучения.',
    request=MatchRequestSerializer,
    responses={200: MatchResponseSerializer},
    tags=['analytics'],
)
@api_view(['POST'])
def match_view(request):
    """
    Calculate match score for user + job.
    POST /api/analytics/match/
    Body: { "user_id": 1, "job_id": 1 }

    Returns match score, matching/missing skills, recommendation, learning path.
    """
    serializer = MatchRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = get_object_or_404(User, pk=serializer.validated_data['user_id'])
    job = get_object_or_404(Job, pk=serializer.validated_data['job_id'])
    profile = get_object_or_404(UserProfile, user=user)

    result = generate_recommendation(profile, job)
    return Response(result)


@extend_schema(
    summary='Сравнение вакансий',
    description='Сравнивает 2-4 вакансии по зарплате, честности, навыкам, обучению. '
                'Если передан user_id — добавляет персонализированный матч-скор и вердикт.',
    request=CompareRequestSerializer,
    responses={200: dict},
    tags=['analytics'],
)
@api_view(['POST'])
def compare_view(request):
    """
    Compare 2-4 jobs side by side.
    POST /api/analytics/compare/
    Body: { "job_ids": [1, 2, 3], "user_id": 1 }  (user_id optional)

    Returns detailed comparison with scores, common/unique skills, and verdict.
    """
    serializer = CompareRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    job_ids = serializer.validated_data['job_ids']
    jobs = list(Job.objects.filter(id__in=job_ids))

    if len(jobs) < 2:
        return Response(
            {'error': 'Need at least 2 valid job IDs'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user_profile = None
    user_id = serializer.validated_data.get('user_id')
    if user_id:
        user = get_object_or_404(User, pk=user_id)
        user_profile = get_object_or_404(UserProfile, user=user)

    result = compare_jobs(jobs, user_profile)
    return Response(result)
