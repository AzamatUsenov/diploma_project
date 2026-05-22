from django.db.models import Avg, Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import CompanyReview, ReviewHelpful
from .serializers import CompanyReviewSerializer, CompanyStatsSerializer


class CompanyReviewViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = CompanyReview.objects.filter(is_approved=True)
        company = self.request.query_params.get('company')
        if company:
            qs = qs.filter(company_name__iexact=company)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'detail': 'Требуется авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        if review.author != request.user:
            return Response({'detail': 'Можно редактировать только свои отзывы'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        if review.author != request.user:
            return Response({'detail': 'Можно удалять только свои отзывы'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='my')
    def my_reviews(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Требуется авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
        qs = CompanyReview.objects.filter(author=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='company-stats')
    def company_stats(self, request):
        company = request.query_params.get('company')
        if not company:
            return Response({'detail': 'Укажите параметр company'}, status=status.HTTP_400_BAD_REQUEST)

        stats = CompanyReview.objects.filter(
            company_name__iexact=company, is_approved=True
        ).aggregate(
            review_count=Count('id'),
            avg_overall=Avg('rating_overall'),
            avg_work_life=Avg('rating_work_life'),
            avg_career_growth=Avg('rating_career_growth'),
            avg_salary=Avg('rating_salary'),
            avg_management=Avg('rating_management'),
        )

        if stats['review_count'] == 0:
            return Response({
                'company_name': company,
                'review_count': 0,
                'avg_overall': 0, 'avg_work_life': 0,
                'avg_career_growth': 0, 'avg_salary': 0,
                'avg_management': 0, 'avg_total': 0,
            })

        avg_total = round(sum(v for k, v in stats.items() if k.startswith('avg_') and v) / 5, 1)
        data = {
            'company_name': company,
            'review_count': stats['review_count'],
            'avg_overall': round(stats['avg_overall'] or 0, 1),
            'avg_work_life': round(stats['avg_work_life'] or 0, 1),
            'avg_career_growth': round(stats['avg_career_growth'] or 0, 1),
            'avg_salary': round(stats['avg_salary'] or 0, 1),
            'avg_management': round(stats['avg_management'] or 0, 1),
            'avg_total': avg_total,
        }
        return Response(CompanyStatsSerializer(data).data)

    @action(detail=True, methods=['post'], url_path='helpful', permission_classes=[IsAuthenticated])
    def toggle_helpful(self, request, pk=None):
        review = self.get_object()
        helpful, created = ReviewHelpful.objects.get_or_create(review=review, user=request.user)
        if not created:
            helpful.delete()
            review.helpful_count = max(0, review.helpful_count - 1)
            review.save(update_fields=['helpful_count'])
            return Response({'helpful': False, 'helpful_count': review.helpful_count})
        review.helpful_count += 1
        review.save(update_fields=['helpful_count'])
        return Response({'helpful': True, 'helpful_count': review.helpful_count})

    @action(detail=False, methods=['get'], url_path='top-companies')
    def top_companies(self, request):
        companies = (
            CompanyReview.objects.filter(is_approved=True)
            .values('company_name')
            .annotate(
                review_count=Count('id'),
                avg_overall=Avg('rating_overall'),
                avg_work_life=Avg('rating_work_life'),
                avg_career_growth=Avg('rating_career_growth'),
                avg_salary=Avg('rating_salary'),
                avg_management=Avg('rating_management'),
            )
            .filter(review_count__gte=1)
            .order_by('-avg_overall')[:20]
        )

        results = []
        for c in companies:
            avg_total = round(
                sum(c[k] for k in ['avg_overall', 'avg_work_life', 'avg_career_growth', 'avg_salary', 'avg_management'] if c[k]) / 5, 1
            )
            results.append({
                'company_name': c['company_name'],
                'review_count': c['review_count'],
                'avg_overall': round(c['avg_overall'] or 0, 1),
                'avg_total': avg_total,
            })

        return Response(results)
