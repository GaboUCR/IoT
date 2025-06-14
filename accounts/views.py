# accounts/views.py
from django.shortcuts       import redirect
from django.urls            import reverse_lazy
from django.views           import View
from django.views.generic   import FormView
from django.contrib.auth    import login
from django.contrib.auth.views import LoginView, LogoutView
from django.views.decorators.csrf import csrf_exempt  


from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .forms                 import StyledAuthenticationForm, SignUpForm

class HomeView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return redirect("login")

class CustomLoginView(LoginView):
    template_name = "accounts/auth.html"
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_login"] = ctx.pop("form")
        ctx["form_signup"] = SignUpForm()
        ctx.setdefault("active_tab", "login")
        return ctx

class SignUpView(FormView):
    template_name = "accounts/auth.html"
    form_class = SignUpForm
    success_url = reverse_lazy("dashboard")

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
        ctx["form_login"] = StyledAuthenticationForm()
        ctx.setdefault("active_tab", "login")
        return ctx

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")

