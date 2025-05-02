# accounts/views.py
from django.urls import reverse_lazy
from django.views.generic import FormView, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from .forms import StyledAuthenticationForm, SignUpForm

class CustomLoginView(LoginView):
    form_class = StyledAuthenticationForm
    template_name = "registration/login.html"
    next_page = reverse_lazy("dashboard")

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")
