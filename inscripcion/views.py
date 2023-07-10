from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User 
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import User
from inscripcion.models import Asignatura 

@login_required
def index(request):
    # Obtener el alumno actualmente autenticado desde la sesión
    alumno = request.user

    # Obtener el semestre actual del alumno
    semestre_actual = alumno.semestre_actual

    # Obtener todos los cursos que pertenecen al semestre actual del alumno
    cursos_listados = Asignatura.objects.filter(semestre=semestre_actual)
    return render(request,"index.html",{'cursos_listados': cursos_listados})




