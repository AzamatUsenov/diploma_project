from django.contrib import admin
from django.utils.html import format_html
from .models import Job, JobTag


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'level', 'salary_range', 'honesty_badge',
                    'is_overqualified', 'is_remote', 'applications_count', 'is_active', 'created_at')
    list_filter = ('level', 'is_remote', 'training_provided', 'is_overqualified', 'is_active', 'company')
    search_fields = ('title', 'company', 'location', 'requirements_text')
    readonly_fields = ('detected_level', 'is_overqualified', 'honesty_score', 'parsed_skills', 'created_at', 'updated_at')
    list_per_page = 25
    list_editable = ('is_active',)
    date_hierarchy = 'created_at'
    actions = ['activate_jobs', 'deactivate_jobs']

    fieldsets = (
        ('Основное', {'fields': ('title', 'company', 'location', 'posted_by', 'is_active')}),
        ('Описание', {'fields': ('description', 'requirements_text')}),
        ('Параметры', {'fields': ('level', 'experience_years', 'salary_min', 'salary_max', 'is_remote', 'training_provided')}),
        ('Технологии', {'fields': ('tech_stack',)}),
        ('Анализ (авто)', {'fields': ('detected_level', 'is_overqualified', 'honesty_score', 'parsed_skills'), 'classes': ('collapse',)}),
        ('Даты', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    @admin.display(description='Зарплата')
    def salary_range(self, obj):
        def fmt(n):
            return f'{n // 1000}K' if n else '?'
        return f'{fmt(obj.salary_min)} – {fmt(obj.salary_max)} сўм'

    @admin.display(description='Честность', ordering='honesty_score')
    def honesty_badge(self, obj):
        score = obj.honesty_score or 0
        if score >= 70:
            color = '#22c55e'
        elif score >= 40:
            color = '#f59e0b'
        else:
            color = '#ef4444'
        return format_html('<span style="color:{}; font-weight:bold">{} %</span>', color, score)

    @admin.display(description='Откликов')
    def applications_count(self, obj):
        return obj.application_set.count()

    @admin.action(description='Активировать выбранные')
    def activate_jobs(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Деактивировать выбранные')
    def deactivate_jobs(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(JobTag)
class JobTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'jobs_count')
    search_fields = ('name',)

    @admin.display(description='Вакансий')
    def jobs_count(self, obj):
        return obj.jobs.count()
