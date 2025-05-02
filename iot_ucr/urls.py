# iot_ucr/urls.py

from django.contrib import admin
from django.urls import path, include
from accounts.views import HomeView, CustomLoginView, SignUpView, CustomLogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),                     # /
    path("login/", CustomLoginView.as_view(), name="login"),       # /login/
    path("signup/", SignUpView.as_view(), name="signup"),          # /signup/
    path("logout/", CustomLogoutView.as_view(), name="logout"),    # /logout/
    path("", include("sensors.urls")),                             # tu dashboard
]
