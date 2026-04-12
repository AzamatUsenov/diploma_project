from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('favorites', views.FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
    path('analyze/<int:job_id>/', views.analyze_job_view, name='analyze-job'),
    path('match/', views.match_view, name='match'),
    path('compare/', views.compare_view, name='compare'),
]
