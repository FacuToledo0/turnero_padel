# reservas/forms.py
from django import forms
from django.utils.timezone import localdate
from django.contrib.auth.models import User
from .models import Reserva
from django.contrib.auth.forms import UserCreationForm
from datetime import date


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class FechaForm(forms.Form):
    fecha = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "min": localdate().strftime("%Y-%m-%d"),  # bloquea fechas pasadas en el calendario
                "class": "form-control"
            }
        ),
        label="Seleccioná la fecha"
    )

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]
        if fecha < localdate():
            raise forms.ValidationError("No se pueden seleccionar fechas pasadas.")
        return fecha


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['cancha', 'fecha', 'hora_inicio', 'hora_fin']
