from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('results', views.TestResultViewSet, basename='testresult')
router.register('code', views.CodeChallengeViewSet, basename='code-challenge')
router.register('', views.SkillTestViewSet, basename='skilltest')

urlpatterns = [
    path('', include(router.urls)),
]
