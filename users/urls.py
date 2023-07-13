from django.urls import path
from . import views

urlpatterns = [
    # #     path('',views.login_view, name='login_view'),
    path('', views.login_users, name='login'),
    path('logout/', views.logout_users, name='logout'),
    path('inscripcion/',views.vista_administrador, name='inscripcion'), 
]
