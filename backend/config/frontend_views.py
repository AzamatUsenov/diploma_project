"""
Simple template views for the frontend pages.
All data is loaded via JavaScript API calls — these just serve the HTML shell.
"""
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'


class JobsListView(TemplateView):
    template_name = 'jobs_list.html'


class JobDetailView(TemplateView):
    template_name = 'job_detail.html'


class CompareView(TemplateView):
    template_name = 'compare.html'


class TestsListView(TemplateView):
    template_name = 'tests_list.html'
