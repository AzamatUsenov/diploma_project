from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer, RegisterSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    CRUD for user profiles.
    list: GET /api/accounts/profiles/
    retrieve: GET /api/accounts/profiles/{id}/
    update: PUT/PATCH /api/accounts/profiles/{id}/
    """
    queryset = UserProfile.objects.select_related('user').all()
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]


class RegisterViewSet(viewsets.GenericViewSet):
    """
    User registration endpoint.
    POST /api/accounts/register/
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        profile = user.profile
        return Response(
            UserProfileSerializer(profile).data,
            status=status.HTTP_201_CREATED,
        )
