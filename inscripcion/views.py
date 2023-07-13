from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import User
from inscripcion.models import Asignatura, Inscripcion
from django.shortcuts import get_object_or_404


@login_required
def index(request):
    # Obtener el alumno actualmente autenticado desde la sesión
    alumno = request.user
    usuario = request.user
    numero_cuenta = alumno.numero_cuenta
    # Obtener el semestre actual del alumno
    semestre_actual = alumno.semestre_actual
    alumno = User.objects.get(numero_cuenta=numero_cuenta)
    asignaturas_inscritas = usuario.alumno.asignatura.all()

    # Obtener todos los cursos que pertenecen al semestre actual del alumno
    cursos_listados = Asignatura.objects.filter(semestre=semestre_actual)
    return render(request, "index.html", context={
        'cursos_listados': cursos_listados,
        'asignaturas_inscritas': asignaturas_inscritas
    })


def inscribir_asignatura(request):
    if request.method == 'POST':
        asignatura_id = request.POST.get('asignatura_id')

        # Obtener el usuario actualmente autenticado
        usuario = request.user

        # Obtener la asignatura a partir del ID
        asignatura = Asignatura.objects.get(clave_asignatura=asignatura_id)

        # Obtener la instancia de Inscripcion del usuario
        inscripcion = usuario.alumno

        # Agregar la asignatura a la relación muchos a muchos utilizando el método set()
        inscripcion.asignatura.add(asignatura)

        return redirect('index')


def eliminar_asignatura(request, asignatura_id):
    if request.method == 'POST':
        # Obtener el usuario actualmente autenticado
        usuario = request.user

        # Obtener la instancia de Inscripcion del usuario
        inscripcion = get_object_or_404(Inscripcion, numero_cuenta=usuario)

        # Obtener la asignatura a partir de la clave_asignatura
        asignatura = get_object_or_404(
            Asignatura, clave_asignatura=asignatura_id)

        # Verificar si la asignatura está en la relación muchos a muchos
        if asignatura in inscripcion.asignatura.all():
            # Eliminar la asignatura de la relación muchos a muchos utilizando el método remove()
            inscripcion.asignatura.remove(asignatura)

    return redirect('index')
