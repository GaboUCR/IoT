# accounts/views.py

from django.shortcuts   import redirect
from django.urls        import reverse_lazy
from django.views       import View
from django.views.generic import TemplateView, FormView
from django.contrib.auth.views import LoginView, LogoutView
from .forms              import StyledAuthenticationForm, SignUpForm

class HomeView(View):
    """
    Raíz de la app: si estoy autenticado voy al dashboard,
    si no, a la pantalla de login/signup.
    """
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return redirect("login")

class CustomLoginView(LoginView):
    template_name = "accounts/auth.html"
    authentication_form = StyledAuthenticationForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # ctx['form'] ya es tu login form, así que lo alias:
        ctx["form_login"]  = ctx.get("form")
        # añadimos el signup vacío
        ctx["form_signup"] = SignUpForm()
        return ctx

class SignUpView(FormView):
    template_name = "accounts/auth.html"
    form_class    = SignUpForm
    success_url   = reverse_lazy("dashboard")

    def form_valid(self, form):
        # crea user + profile
        form.save()
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_login"] = StyledAuthenticationForm()
        return ctx

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")
