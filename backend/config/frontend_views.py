from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'


class JobsListView(TemplateView):
    template_name = 'jobs_list.html'


class JobDetailView(TemplateView):
    template_name = 'job_detail.html'


class JobCreateView(TemplateView):
    template_name = 'job_create.html'


class CompareView(TemplateView):
    template_name = 'compare.html'


class TestsListView(TemplateView):
    template_name = 'tests_list.html'


class LoginView(TemplateView):
    template_name = 'login.html'


class RegisterView(TemplateView):
    template_name = 'register.html'


class ProfileView(TemplateView):
    template_name = 'profile.html'


class PublicProfileView(TemplateView):
    template_name = 'public_profile.html'


class ApplicationsView(TemplateView):
    template_name = 'applications.html'


class FavoritesView(TemplateView):
    template_name = 'favorites.html'
