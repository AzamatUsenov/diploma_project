from django.contrib import admin
from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title', 'job_company', 'created_at')
    list_filter = ('job__company', 'created_at')
    search_fields = ('user__username', 'job__title', 'job__company')
    raw_id_fields = ('user', 'job')
    date_hierarchy = 'created_at'
    list_per_page = 25

    @admin.display(description='Вакансия', ordering='job__title')
    def job_title(self, obj):
        return obj.job.title

    @admin.display(description='Компания', ordering='job__company')
    def job_company(self, obj):
        return obj.job.company
