from rest_framework import serializers
from .models import Application, Message, Interview
from accounts.serializers import UserProfileSerializer


class ApplicationListSerializer(serializers.ModelSerializer):
    applicant_username = serializers.CharField(source='applicant.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_company = serializers.CharField(source='job.company', read_only=True)
    applicant_profile = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id', 'applicant', 'applicant_username',
            'job', 'job_title', 'job_company',
            'cover_letter', 'status', 'created_at',
            'applicant_profile',
        ]
        read_only_fields = ['applicant', 'status', 'created_at']

    def get_applicant_profile(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'profile') and request.user.profile.role == 'hr':
            if hasattr(obj.applicant, 'profile'):
                return UserProfileSerializer(obj.applicant.profile).data
        return None


class ApplicationDetailSerializer(serializers.ModelSerializer):
    applicant_username = serializers.CharField(source='applicant.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_company = serializers.CharField(source='job.company', read_only=True)
    applicant_profile = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id', 'applicant', 'applicant_username',
            'job', 'job_title', 'job_company',
            'cover_letter', 'status',
            'created_at', 'updated_at',
            'applicant_profile',
        ]
        read_only_fields = ['applicant', 'created_at', 'updated_at']

    def get_applicant_profile(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'profile') and request.user.profile.role == 'hr':
            if hasattr(obj.applicant, 'profile'):
                return UserProfileSerializer(obj.applicant.profile).data
        return None


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['job', 'cover_letter']


class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['status']


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_role = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'application', 'sender', 'sender_username', 'sender_role',
                  'text', 'is_read', 'created_at']
        read_only_fields = ['sender', 'application', 'created_at', 'is_read']

    def get_sender_role(self, obj):
        if hasattr(obj.sender, 'profile'):
            return obj.sender.profile.role
        return None


class MessageCreateSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=2000)


class InterviewSerializer(serializers.ModelSerializer):
    applicant_username = serializers.CharField(source='application.applicant.username', read_only=True)
    job_title = serializers.CharField(source='application.job.title', read_only=True)

    class Meta:
        model = Interview
        fields = [
            'id', 'application', 'applicant_username', 'job_title',
            'scheduled_at', 'duration_minutes', 'status', 'notes',
            'location', 'created_at',
        ]
        read_only_fields = ['created_at']


class InterviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['application', 'scheduled_at', 'duration_minutes', 'notes', 'location']
