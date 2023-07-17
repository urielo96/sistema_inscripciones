from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import User
from inscripcion.models import Asignatura, Inscripcion , Grupo
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.views import View


from django.http import FileResponse
from django.template.loader import render_to_string
from django.utils.text import slugify

def user_authenticated(user):
    return user.is_authenticated

@user_passes_test(user_authenticated, login_url='/users/login')
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

def redirect_to_login_if_expired(view_func):
    decorated_view_func = user_passes_test(user_authenticated, login_url='/users/login')(view_func)
    
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.session.get_expiry_age() <= 0:
            return redirect('/users/login')
        return decorated_view_func(request, *args, **kwargs)

    return wrapper

index = redirect_to_login_if_expired(index)

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


def usuarios_inscritos_grupo(request):
    grupos = Grupo.objects.all()
    grupo_seleccionado = None
    usuarios_inscritos = []

    if 'grupo' in request.GET:
        grupo_clave = int(request.GET['grupo'])
        grupo_seleccionado = Grupo.objects.get(clave_grupo=grupo_clave)
        asignaturas_grupo = grupo_seleccionado.asignaturas.all()
        usuarios_inscritos = User.objects.filter(alumno__asignatura__in=asignaturas_grupo).distinct()

    context = {
        'grupos': grupos,
        'grupo_seleccionado': grupo_seleccionado,
        'usuarios': usuarios_inscritos
    }

    return render(request, 'usuarios_inscritos_grupo.html', context)



from django.http import HttpResponse


def generar_archivo_txt(request, grupo_clave):
    grupo_seleccionado = Grupo.objects.get(clave_grupo=grupo_clave)
    clave_asignatura = request.GET.get('asignatura')  # Obtenemos la clave de la asignatura de los parámetros de la URL
    asignatura_especifica = grupo_seleccionado.asignaturas.get(clave_asignatura=clave_asignatura)
    usuarios_inscritos = User.objects.filter(alumno__asignatura=asignatura_especifica).distinct()

    contenido = ""

    for usuario in usuarios_inscritos:
        linea = f"{usuario.numero_cuenta}0723{grupo_seleccionado.clave_grupo}{asignatura_especifica.clave_asignatura}A\n"
        contenido += linea

    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="alumnos_grupo.txt"'
    response.write(contenido)

    return response



