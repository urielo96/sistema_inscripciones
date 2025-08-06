from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # #     path('',views.login_view, name='login_view'),
    path('', RedirectView.as_view(pattern_name='login'), name='index'),
    path('users/login/', views.login_users, name='login'),
    path('logout/', views.logout_users, name='logout'),
    path('capturar_email/', views.capturar_email, name='capturar_email'),
    path('grupos/',views.vista_administrador, name='inscripcion'), 
    path('carga_users/',views.carga_users, name='carga_users'),
    path('crear_periodo/',views.crear_periodo, name='crear_periodo'),
    path('historial_inscripciones/',views.ver_historial_inscripciones, name='historial_inscripciones'),
]
