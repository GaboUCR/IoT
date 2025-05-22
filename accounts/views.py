# accounts/views.py
from django.shortcuts       import redirect
from django.urls            import reverse_lazy
from django.views           import View
from django.views.generic   import FormView
from django.contrib.auth    import login
from django.contrib.auth.views import LoginView, LogoutView
from .forms                 import StyledAuthenticationForm, SignUpForm
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.views import View
from .models import Profile


class HomeView(View):
    """
    /
    Si el usuario ya está logueado → dashboard,
    si no, → /login/
    """
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return redirect("login")


class CustomLoginView(LoginView):
    """
    /login/
    Usa StyledAuthenticationForm y envía también un SignUpForm vacío
    para que auth.html pueda renderizar ambos formularios.
    """
    template_name         = "accounts/auth.html"
    authentication_form   = StyledAuthenticationForm
    redirect_authenticated_user = True  # evita volver al login si ya está dentro

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_login"]  = ctx.pop("form")
        ctx["form_signup"] = SignUpForm()
        ctx.setdefault("active_tab", "login")

        return ctx


class SignUpView(FormView):
    template_name = "accounts/auth.html"
    form_class    = SignUpForm
    success_url   = reverse_lazy("dashboard")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        ctx = self.get_context_data(form=form)
        ctx["active_tab"] = "signup"
        return self.render_to_response(ctx)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_signup"] = ctx.pop("form")
        ctx["form_login"]  = StyledAuthenticationForm()
        ctx.setdefault("active_tab", "login")
        return ctx

class CustomLogoutView(LogoutView):
    """
    /logout/
    Solo cierra sesión y redirige al login.
    """
    next_page = reverse_lazy("login")

class GuestLoginView(View):
    def post(self, request, *args, **kwargs):

        User = get_user_model()
        username = settings.GUEST_USERNAME

        guest, created = User.objects.get_or_create(
            username=username,
            defaults={"first_name": "Invitado", "email": ""}
        )

        # Siempre asegúrate de que tenga un Profile
        if not hasattr(guest, 'profile'):
            Profile.objects.create(user=guest, license="1234")

        guest.set_unusable_password()
        guest.save()
        login(request, guest)
        return redirect("dashboard")
