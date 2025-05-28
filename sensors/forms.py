from django import forms
from .models import Sensor, Actuator

class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = ['name', 'sensor_type', 'unit', 'topic']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full', 'placeholder': 'Nombre del sensor'}),
            'sensor_type': forms.TextInput(attrs={'class': 'mt-1 block w-full', 'placeholder': 'Tipo de dato'}),
            'unit': forms.TextInput(attrs={'class': 'mt-1 block w-full', 'placeholder': 'Unidad'}),
            'topic': forms.TextInput(attrs={'class': 'mt-1 block w-full', 'placeholder': 'Tópico MQTT'}),
        }

class ActuatorForm(forms.ModelForm):
    class Meta:
        model = Actuator
        fields = ['name', 'actuator_type', 'topic']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full', 'placeholder': 'Nombre del actuador'}),
            'actuator_type': forms.Select(attrs={'class': 'mt-1 block w-full'}),
            'topic': forms.TextInput(attrs={'class': 'mt-1 block w-full', 'placeholder': 'Tópico MQTT'}),
        }
