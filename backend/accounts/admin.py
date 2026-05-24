from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = 'Профиль'
    verbose_name_plural = 'Профиль'
    fieldsets = (
        ('Основное', {'fields': ('role', 'level', 'bio', 'avatar')}),
        ('Навыки', {'fields': ('skills',)}),
        ('Соискатель', {'fields': ('portfolio_url', 'github_url'), 'classes': ('collapse',)}),
        ('HR', {'fields': ('company_name', 'company_description'), 'classes': ('collapse',)}),
    )


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'get_role', 'get_level', 'get_company', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'profile__role', 'profile__level')
    search_fields = ('username', 'email', 'profile__company_name')

    @admin.display(description='Роль', ordering='profile__role')
    def get_role(self, obj):
        try:
            return {'applicant': 'Соискатель', 'hr': 'HR'}[obj.profile.role]
        except UserProfile.DoesNotExist:
            return '-'

    @admin.display(description='Уровень', ordering='profile__level')
    def get_level(self, obj):
        try:
            return obj.profile.level or '-'
        except UserProfile.DoesNotExist:
            return '-'

    @admin.display(description='Компания')
    def get_company(self, obj):
        try:
            return obj.profile.company_name or '-'
        except UserProfile.DoesNotExist:
            return '-'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'level', 'company_name', 'skills_count', 'created_at')
    list_filter = ('role', 'level', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name', 'bio')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

    @admin.display(description='Навыков')
    def skills_count(self, obj):
        return len(obj.skills) if obj.skills else 0
