from django.contrib import admin
from django.utils.html import format_html
from .models import Application, Message


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job_title', 'company', 'status_badge', 'cover_preview', 'created_at')
    list_filter = ('status', 'job__company', 'job__level', 'created_at')
    search_fields = ('applicant__username', 'job__title', 'job__company', 'cover_letter')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    date_hierarchy = 'created_at'
    list_editable = ()
    actions = ['mark_accepted', 'mark_rejected', 'mark_reviewed']
    raw_id_fields = ('applicant', 'job')

    fieldsets = (
        ('Заявка', {'fields': ('applicant', 'job', 'status')}),
        ('Сопроводительное', {'fields': ('cover_letter',)}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )

    @admin.display(description='Вакансия', ordering='job__title')
    def job_title(self, obj):
        return obj.job.title

    @admin.display(description='Компания', ordering='job__company')
    def company(self, obj):
        return obj.job.company

    @admin.display(description='Статус', ordering='status')
    def status_badge(self, obj):
        colors = {
            'pending': ('#f59e0b', 'Ожидает'),
            'reviewed': ('#3b82f6', 'Просмотрено'),
            'accepted': ('#22c55e', 'Принято'),
            'rejected': ('#ef4444', 'Отклонено'),
        }
        color, label = colors.get(obj.status, ('#9ca3af', obj.status))
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; border-radius:10px; font-size:11px">{}</span>',
            color, label)

    @admin.display(description='Письмо')
    def cover_preview(self, obj):
        if obj.cover_letter:
            return obj.cover_letter[:80] + ('...' if len(obj.cover_letter) > 80 else '')
        return '-'

    @admin.action(description='Принять выбранные')
    def mark_accepted(self, request, queryset):
        queryset.update(status='accepted')

    @admin.action(description='Отклонить выбранные')
    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected')

    @admin.action(description='Отметить как просмотренные')
    def mark_reviewed(self, request, queryset):
        queryset.update(status='reviewed')


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'text', 'is_read', 'created_at')
    can_delete = False


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'application', 'text_short', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'text')
    readonly_fields = ('created_at',)
    list_per_page = 50

    @admin.display(description='Текст')
    def text_short(self, obj):
        return obj.text[:80] + ('...' if len(obj.text) > 80 else '')
