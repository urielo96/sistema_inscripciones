from django.shortcuts import render,redirect
# from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
# from .models import Alumno, Asignatura
# from django.contrib.auth import login,logout,authenticate
# from django.contrib.auth.models import User 
# from django.db import IntegrityError
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages


def index(request):
    return render(request,"index.html")


# # def inscripcion(request):
# #     asignaturas_listadas = Asignatura.objects.all()
# #     return render(request,"inscripcion.html", {"asignaturas" : asignaturas_listadas} )



# def login_view(request):
#     if request.method == 'POST':
#         numero_cuenta = request.POST.get('numero_cuenta')
#         password = request.POST.get('password')

#         user = Alumno.objects.filter(numero_cuenta=numero_cuenta).first()
#         if user is not None:
#             login(request,user)
#             user = authenticate(request, username=user.username, password=password)

#             if user is not None:
#                 # El usuario ha sido autenticado correctamente
#                 # Realizar las acciones necesarias, como iniciar sesión y redirigir al usuario a la página principal
#                 ...
#             else:
                
#                 # Las credenciales son incorrectas
#                 context = {'error': 'Credenciales Incorrectas'}
#                 return render(request, "login_view.html", context)
#         else:
#             # No se encontró un usuario con el número de cuenta especificado
#             context = {'error': 'Credenciales Incorrectas'}
#             return render(request, "login_view.html", context)

#     return render(request, 'login_view.html', {})
    
