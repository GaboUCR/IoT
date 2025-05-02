# accounts/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common = "mt-1 block w-full border-gray-300 rounded px-3 py-2"
        self.fields["username"].widget.attrs.update({
            "class": common,
            "placeholder": "Usuario"
        })
        self.fields["password"].widget.attrs.update({
            "class": common,
            "placeholder": "Contraseña"
        })
