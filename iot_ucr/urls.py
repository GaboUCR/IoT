# iot_ucr/urls.py

from django.contrib import admin
from django.urls import path, include
from accounts.views import HomeView

urlpatterns = [
    path("",       HomeView.as_view(),    name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("sensors.urls")), 
]
