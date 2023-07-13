from django.urls import path
from . import views

urlpatterns = [
    # #     path('',views.login_view, name='login_view'),
    path('users/login/', views.login_users, name='login'),
    path('logout/', views.logout_users, name='logout'),
    path('grupos/',views.vista_administrador, name='inscripcion'), 
]
