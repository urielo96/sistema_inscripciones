# forms.py
from django import forms
from .models import User


class Carga_alumnos(forms.Form):
    file = forms.FileField(label='Carga el Archivo de Alumnos')


class EmailForm(forms.ModelForm):
    email_requerido = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'ejemplo@gmail.com',
            'required': True
        }),
        help_text='Por favor, proporciona tu correo electrónico para continuar.'
    )
    
    class Meta:
        model = User
        fields = ['email_requerido']