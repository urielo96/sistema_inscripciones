from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from inscripcion.models import Inscripcion


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from . forms import Carga_alumnos
import openpyxl
from django.contrib.auth.hashers import make_password
from .models import User
from django.shortcuts import render

def login_users(request):
    if request.method == 'POST':
        numero_cuenta = request.POST['numero_cuenta']
        password = request.POST['password']
        user = authenticate(request, username=numero_cuenta, password=password)

        if user is not None:
            login(request, user)

            try:
                # Intentar obtener la instancia de Inscripcion del usuario
                inscripcion = user.alumno
            except ObjectDoesNotExist:
                # Si no existe la instancia de Inscripcion, crearla
                inscripcion = Inscripcion(numero_cuenta=user)
                inscripcion.save()

            # Verificar si el usuario es administrativo
            if user.groups.filter(name='Administrativos').exists():
                return redirect('usuarios_inscritos_grupo')

            return redirect('index')
        else:
            messages.error(request, 'Número de Cuenta o contraseña inválidos')

    return render(request, 'authenticate/login_view.html', {'messages': messages.get_messages(request)})


def logout_users(request):
    logout(request)
    # Lógica adicional después del cierre de sesión
    return redirect('login')


def es_administrador(user):
    return user.is_authenticated and user.is_superuser


@user_passes_test(es_administrador)
def vista_administrador(request):
    # Código de la vista para el administrador aquí
    return render(request, 'authenticate/inscripcion.html', {'messages': messages.get_messages(request)})
    

from django.contrib import messages
import openpyxl

def carga_users(request):
    if request.method == 'POST':
        form = Carga_alumnos(request.POST, request.FILES)
        if form.is_valid():
            try:
                archivo = openpyxl.load_workbook(request.FILES['file'])
                
                for hoja in archivo.worksheets:  # Iterar sobre todas las hojas
                    for fila in hoja.iter_rows(min_row=2, values_only=True):
                        if fila[2] is not None:
                            numero_cuenta = fila[1]
                            nombre_completo = fila[2]
                            
                            # Verificar si el usuario ya existe por número de cuenta
                            if User.objects.filter(numero_cuenta=numero_cuenta).exists():
                                messages.warning(request, f'El usuario con número de cuenta {numero_cuenta} {nombre_completo} ya tiene una cuenta.')
                                continue
                            
                            # Verificar que nombre_completo sea una cadena antes de intentar dividirlo
                            if not isinstance(nombre_completo, str):
                                messages.error(request, f'Error en la fila: {fila}. El nombre completo no es una cadena.')
                                continue
                            
                            # Separar el nombre completo en nombre y apellidos
                            nombre_partes = nombre_completo.split()
                            if len(nombre_partes) < 2:
                                apellido_paterno = ''
                                apellido_materno = ''
                                nombre_final = nombre_partes[0] if nombre_partes else ''
                            elif len(nombre_partes) == 2:
                                nombre_final = nombre_partes[0]
                                apellido_paterno = nombre_partes[1]
                                apellido_materno = ''
                            else:
                                nombre_final = nombre_partes[0]
                                apellido_paterno = nombre_partes[1]
                                apellido_materno = ' '.join(nombre_partes[2:])
                            
                            # Generar un username único
                            base_username = '_'.join(nombre_partes)
                            username = base_username
                            contador = 1
                            while User.objects.filter(username=username).exists():
                                username = f"{base_username}_{contador}"
                                contador += 1
                            
                            semestre_actual = 1
                            is_superuser = False
                            is_staff = False
                            is_active = True
                            email = fila[3] if fila[3] else 'default@example.com'
                            first_name = nombre_final
                            last_name = f"{apellido_paterno} {apellido_materno}"

                            # Crear y guardar la instancia del modelo User
                            if numero_cuenta is not None:
                                usuario = User.objects.create(
                                    numero_cuenta=numero_cuenta,
                                    password='contrasena_codificada',  # Asegúrate de definir contrasena_codificada
                                    is_superuser=is_superuser,
                                    username=username,
                                    first_name=first_name,
                                    last_name=last_name,
                                    email=email,
                                    is_staff=is_staff,
                                    is_active=is_active,
                                    semestre_actual=semestre_actual
                                )
                                messages.success(request, f'El usuario {first_name} {last_name} ha sido registrado exitosamente.')
                            
                            # Inscribir al alumno en las materias
                            for col in range(4, len(fila), 3):  # Asumiendo que cada materia ocupa 3 columnas (CVE, Asignatura, Grupo)
                                cve = fila[col]
                                asignatura = fila[col + 1]
                                grupo = fila[col + 2]
                                
                                if cve and asignatura and grupo:
                                    # Buscar o crear la materia en la base de datos
                                    materia, created = Materia.objects.get_or_create(
                                        cve=cve,
                                        nombre=asignatura,
                                        grupo=grupo
                                    )
                                    # Asociar la materia al usuario
                                    usuario.materias.add(materia)  # Asumiendo una relación ManyToMany
                                    messages.success(request, f'{first_name} {last_name} inscrito en {asignatura}.')
                            else:
                                messages.error(request, 'El número de cuenta no puede ser nulo.')
            except Exception as e:
                messages.error(request, f'Error al cargar el alumno: {str(e)}')
    else:
        form = Carga_alumnos()
    
    return render(request, 'carga_alumnos.html', {'form': form})

