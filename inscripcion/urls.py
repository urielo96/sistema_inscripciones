from django.urls import path
from . import views

urlpatterns = [
    # #     path('',views.login_view, name='login_view'),
    path('index/', views.index, name='index'),
    path('inscribr_asignatura/', views.inscribir_asignatura,
         name='inscribir_asignatura'),
    path('eliminar_asignatura/<int:asignatura_id>/',
         views.eliminar_asignatura, name='eliminar_asignatura'),
       

]
