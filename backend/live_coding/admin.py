from django.contrib import admin
from .models import LiveSession, SessionResult


@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ['invite_code', 'title', 'hr', 'candidate', 'status', 'created_at']
    list_filter = ['status']
    readonly_fields = ['id', 'invite_code']


@admin.register(SessionResult)
class SessionResultAdmin(admin.ModelAdmin):
    list_display = ['session', 'question', 'status', 'tests_passed', 'tests_total']
