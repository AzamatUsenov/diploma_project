from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'role', 'level', 'avatar', 'bio', 'skills',
            'portfolio_url', 'github_url', 'resume',
            'company_name', 'company_description',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(choices=['applicant', 'hr'], default='applicant')
    level = serializers.ChoiceField(choices=['junior', 'mid', 'senior'], default='junior', required=False)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists')
        return value

    def create(self, validated_data):
        role = validated_data.pop('role', 'applicant')
        level = validated_data.pop('level', 'junior')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        UserProfile.objects.create(user=user, role=role, level=level)
        return user
