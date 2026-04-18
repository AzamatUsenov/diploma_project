from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .frontend_views import (
    IndexView, JobsListView, JobDetailView, JobCreateView,
    CompareView, TestsListView,
    LoginView, RegisterView, ProfileView, ApplicationsView, FavoritesView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # REST API
    path('api/accounts/', include('accounts.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/applications/', include('applications.urls')),
    path('api/tests/', include('tests_system.urls')),
    path('api/analytics/', include('analytics.urls')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Frontend pages
    path('', IndexView.as_view(), name='home'),
    path('jobs/', JobsListView.as_view(), name='jobs'),
    path('jobs/create/', JobCreateView.as_view(), name='job_create'),
    path('jobs/<int:pk>/', JobDetailView.as_view(), name='job_detail'),
    path('compare/', CompareView.as_view(), name='compare'),
    path('tests/', TestsListView.as_view(), name='tests'),
    path('login/', LoginView.as_view(), name='frontend_login'),
    path('register/', RegisterView.as_view(), name='frontend_register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('applications/', ApplicationsView.as_view(), name='applications'),
    path('favorites/', FavoritesView.as_view(), name='favorites'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
