# accounts/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings


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


class SignUpForm(UserCreationForm):
    license = forms.CharField(
        max_length=64,
        label="Licencia de registro",
        help_text="Introduce tu código de licencia para activar la cuenta",
        widget=forms.TextInput(attrs={
            "placeholder": "Código de licencia"
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "license")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common_classes = "mt-1 block w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholders = {
            "username": "Usuario",
            "email": "Correo electrónico",
            "password1": "Contraseña",
            "password2": "Confirmar contraseña",
            "license": "Código de licencia",
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({
                "class": common_classes,
                "placeholder": placeholders.get(name, "")
            })
            if name.startswith("password"):
                field.help_text = None

    def save(self, commit=True):
        # 1) Crea el User
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # 2) La señal post_save ya habrá creado el Profile vacío,
            #    ahora lo actualizamos con la license
            user.profile.license = self.cleaned_data["license"]
            user.profile.save()
        return user

    def clean_license(self):
        codigo = self.cleaned_data.get("license")
        if codigo != settings.SIGNUP_LICENSE:
            raise ValidationError("License code is not valid!")
        return codigo