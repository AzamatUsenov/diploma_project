from django.contrib import admin
from .models import SkillTest, Question, TestResult, Answer

@admin.register(SkillTest)
class SkillTestAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'difficulty', 'created_at')
    list_filter = ('language', 'difficulty')
    search_fields = ('title',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('test', 'question_type', 'order')
    list_filter = ('test', 'question_type')

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score', 'status', 'completed_at')
    list_filter = ('status', 'completed_at')
    search_fields = ('user__username', 'test__title')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('result', 'question', 'is_correct')
    list_filter = ('is_correct',)
