from django import forms
from .models import Sensor, Actuator

COMMON_INPUT = {
    'class': 'mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2',
}

class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = ['name', 'sensor_type', 'unit', 'topic']
        widgets = {
            'name': forms.TextInput(attrs={**COMMON_INPUT, 'placeholder': 'Nombre del sensor'}),
            'sensor_type': forms.TextInput(attrs={**COMMON_INPUT, 'placeholder': 'Tipo de dato'}),
            'unit': forms.TextInput(attrs={**COMMON_INPUT, 'placeholder': 'Unidad'}),
            'topic': forms.TextInput(attrs={**COMMON_INPUT, 'placeholder': 'Tópico MQTT'}),
        }

class ActuatorForm(forms.ModelForm):
    class Meta:
        model = Actuator
        fields = ['name', 'actuator_type', 'topic']
        widgets = {
            'name': forms.TextInput(attrs={**COMMON_INPUT, 'placeholder': 'Nombre del actuador'}),
            'actuator_type': forms.Select(attrs={**COMMON_INPUT}),
            'topic': forms.TextInput(attrs={**COMMON_INPUT, 'placeholder': 'Tópico MQTT'}),
        }