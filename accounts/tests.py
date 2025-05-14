# accounts/tests.py

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from .models import Profile
from .forms import SignUpForm

class ProfileModelTest(TestCase):
    def test_profile_created_on_user_save(self):
        user = User.objects.create_user(username="juan", password="123")
        # La señal post_save debe haber creado el Profile
        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, Profile)
        self.assertEqual(str(user.profile), "Perfil de juan")

class SignUpFormTest(TestCase):
    def setUp(self):
        settings.SIGNUP_LICENSE = "ABC123"

    def test_clean_license_valid(self):
        form = SignUpForm(data={
            "username": "maria",
            "email": "m@x.com",
            "password1": "complexpass123",
            "password2": "complexpass123",
            "license": "ABC123",
        })
        self.assertTrue(form.is_valid())

    def test_clean_license_invalid(self):
        form = SignUpForm(data={
            "username": "maria",
            "email": "m@x.com",
            "password1": "complexpass123",
            "password2": "complexpass123",
            "license": "WRONG",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("license", form.errors)

    def test_save_creates_profile_with_license(self):
        settings.SIGNUP_LICENSE = "XYZ999"
        form = SignUpForm(data={
            "username": "luis",
            "email": "l@x.com",
            "password1": "complexpass123",
            "password2": "complexpass123",
            "license": "XYZ999",
        })
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.profile.license, "XYZ999")

class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="demo", password="pass")

    def test_redirects_to_login_when_anonymous(self):
        resp = self.client.get(reverse("home"))
        self.assertRedirects(resp, reverse("login"))

    def test_redirects_to_dashboard_when_logged_in(self):
        self.client.login(username="demo", password="pass")
        resp = self.client.get(reverse("home"))
        self.assertRedirects(resp, reverse("dashboard"))
