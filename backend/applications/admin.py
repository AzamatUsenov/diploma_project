from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('applicant__username', 'job__title')
    readonly_fields = ('created_at', 'updated_at')
