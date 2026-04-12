from django.contrib import admin
from .models import Job, JobTag

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'level', 'is_remote', 'honesty_score', 'created_at', 'is_active')
    list_filter = ('level', 'is_remote', 'training_provided', 'is_overqualified', 'is_active')
    search_fields = ('title', 'company', 'location')
    readonly_fields = ('detected_level', 'is_overqualified', 'honesty_score', 'parsed_skills', 'created_at', 'updated_at')

@admin.register(JobTag)
class JobTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
