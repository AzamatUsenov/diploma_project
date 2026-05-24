from django.contrib import admin
from django.utils.html import format_html
from .models import SkillTest, Question, TestResult, Answer, CodeSubmission


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ('order', 'question_type', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')
    ordering = ('order',)


@admin.register(SkillTest)
class SkillTestAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'difficulty_badge', 'questions_count', 'results_count', 'created_at')
    list_filter = ('language', 'difficulty')
    search_fields = ('title', 'description')
    inlines = [QuestionInline]
    list_per_page = 25

    @admin.display(description='Сложность')
    def difficulty_badge(self, obj):
        colors = {'easy': '#22c55e', 'medium': '#f59e0b', 'hard': '#ef4444'}
        labels = {'easy': 'Лёгкий', 'medium': 'Средний', 'hard': 'Сложный'}
        color = colors.get(obj.difficulty, '#9ca3af')
        label = labels.get(obj.difficulty, obj.difficulty)
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; border-radius:10px; font-size:11px">{}</span>',
            color, label)

    @admin.display(description='Вопросов')
    def questions_count(self, obj):
        return obj.question_set.count()

    @admin.display(description='Пройдено')
    def results_count(self, obj):
        return obj.testresult_set.count()


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'test', 'question_type', 'correct_answer', 'order')
    list_filter = ('test', 'question_type')
    search_fields = ('text',)
    list_per_page = 50

    @admin.display(description='Вопрос')
    def short_text(self, obj):
        return obj.text[:70] + ('...' if len(obj.text) > 70 else '')


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'user_answer', 'is_correct')
    can_delete = False


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score_display', 'status_badge', 'duration_display', 'completed_at')
    list_filter = ('status', 'test', 'completed_at')
    search_fields = ('user__username', 'test__title')
    readonly_fields = ('started_at', 'completed_at')
    inlines = [AnswerInline]
    list_per_page = 25

    @admin.display(description='Результат', ordering='score')
    def score_display(self, obj):
        pct = round(obj.score / obj.max_score * 100) if obj.max_score else 0
        return f'{obj.score}/{obj.max_score} ({pct}%)'

    @admin.display(description='Статус')
    def status_badge(self, obj):
        color = '#22c55e' if obj.status == 'passed' else '#ef4444'
        label = 'Сдан' if obj.status == 'passed' else 'Не сдан'
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; border-radius:10px; font-size:11px">{}</span>',
            color, label)

    @admin.display(description='Время')
    def duration_display(self, obj):
        if obj.duration_seconds:
            m, s = divmod(obj.duration_seconds, 60)
            return f'{m} мин {s} сек'
        return '-'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('result', 'question_short', 'user_answer', 'is_correct_icon')
    list_filter = ('is_correct', 'result__test')
    search_fields = ('result__user__username',)
    list_per_page = 50

    @admin.display(description='Вопрос')
    def question_short(self, obj):
        return obj.question.text[:50]

    @admin.display(description='Верно', boolean=True)
    def is_correct_icon(self, obj):
        return obj.is_correct


@admin.register(CodeSubmission)
class CodeSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'question_short', 'status_badge', 'tests_display', 'execution_time_ms', 'created_at')
    list_filter = ('status', 'question__test')
    search_fields = ('user__username', 'question__text')
    readonly_fields = ('user', 'question', 'code', 'status', 'output', 'test_results',
                       'tests_passed', 'tests_total', 'execution_time_ms', 'error_message', 'created_at')
    list_per_page = 25

    @admin.display(description='Задача')
    def question_short(self, obj):
        return obj.question.text[:50]

    @admin.display(description='Статус')
    def status_badge(self, obj):
        colors = {'passed': '#22c55e', 'failed': '#f59e0b', 'error': '#ef4444', 'timeout': '#8b5cf6'}
        color = colors.get(obj.status, '#9ca3af')
        return format_html(
            '<span style="background:{}; color:white; padding:2px 8px; border-radius:10px; font-size:11px">{}</span>',
            color, obj.get_status_display())

    @admin.display(description='Тесты')
    def tests_display(self, obj):
        if obj.tests_total == 0:
            return '-'
        return f'{obj.tests_passed}/{obj.tests_total}'
