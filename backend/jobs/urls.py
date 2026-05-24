from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('tags', views.JobTagViewSet)
router.register('', views.JobViewSet, basename='job')

urlpatterns = [
    path('company-info/', views.company_info_view, name='company-info'),
    path('', include(router.urls)),
]
