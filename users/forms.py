# forms.py
from django import forms


class Carga_alumnos(forms.Form):
    file = forms.FileField(label='Carga el Archivo de Alumnos')