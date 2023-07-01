from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Asignatura


def home(request):
    asignaturas_listadas = Asignatura.objects.all()
    return render(request, "index.html", {"asignaturas" : asignaturas_listadas} )



def login(request):
    return render (request,'signup.html', {'form': UserCreationForm})
