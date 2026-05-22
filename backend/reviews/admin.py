from django.contrib import admin
from .models import CompanyReview, ReviewHelpful


@admin.register(CompanyReview)
class CompanyReviewAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'author', 'rating_overall', 'is_anonymous', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'is_anonymous', 'rating_overall']
    search_fields = ['company_name', 'title', 'author__username']
    list_editable = ['is_approved']


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'created_at']
