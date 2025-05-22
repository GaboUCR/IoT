# accounts/urls.py
from django.urls import path
from .views       import HomeView, CustomLoginView, SignUpView, CustomLogoutView, GuestLoginView

urlpatterns = [
    path("",       HomeView.as_view(),    name="home"),    # /
    path("login/",  CustomLoginView.as_view(), name="login"),
    path("signup/", SignUpView.as_view(),       name="signup"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("login/guest/", GuestLoginView.as_view(), name="guest-login"),
]
