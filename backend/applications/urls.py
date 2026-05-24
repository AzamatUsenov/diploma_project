from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.ApplicationViewSet, basename='application')

interview_router = DefaultRouter()
interview_router.register('', views.InterviewViewSet, basename='interview')

urlpatterns = [
    path('stats/', views.hr_stats_view, name='hr-stats'),
    path('interviews/', include(interview_router.urls)),
    path('', include(router.urls)),
]
