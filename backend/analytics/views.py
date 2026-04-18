from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes as perm_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
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
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.select_related('job', 'user').filter(
            user=self.request.user
        )

    def create(self, request):
        serializer = FavoriteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job = get_object_or_404(Job, pk=serializer.validated_data['job_id'])
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, job=job,
        )
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
@perm_classes([IsAuthenticatedOrReadOnly])
def analyze_job_view(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    analysis = analyze_job(job)

    job.parsed_skills = analysis['parsed_skills']
    job.detected_level = analysis['detected_level']
    job.is_overqualified = analysis['is_overqualified']
    job.honesty_score = analysis['honesty_score']
    job.save(update_fields=['parsed_skills', 'detected_level', 'is_overqualified', 'honesty_score'])

    return Response(analysis)


@extend_schema(
    summary='Матчинг пользователя и вакансии',
    description='Рассчитывает процент совпадения навыков пользователя с требованиями вакансии.',
    request=MatchRequestSerializer,
    responses={200: MatchResponseSerializer},
    tags=['analytics'],
)
@api_view(['POST'])
@perm_classes([IsAuthenticated])
def match_view(request):
    serializer = MatchRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    job = get_object_or_404(Job, pk=serializer.validated_data['job_id'])
    profile = request.user.profile

    result = generate_recommendation(profile, job)
    return Response(result)


@extend_schema(
    summary='Сравнение вакансий',
    description='Сравнивает 2-4 вакансии по зарплате, честности, навыкам, обучению.',
    request=CompareRequestSerializer,
    responses={200: dict},
    tags=['analytics'],
)
@api_view(['POST'])
@perm_classes([IsAuthenticated])
def compare_view(request):
    serializer = CompareRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    job_ids = serializer.validated_data['job_ids']
    jobs = list(Job.objects.filter(id__in=job_ids))

    if len(jobs) < 2:
        return Response(
            {'error': 'Need at least 2 valid job IDs'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user_profile = request.user.profile
    result = compare_jobs(jobs, user_profile)
    return Response(result)
