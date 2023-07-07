from django.urls import path
from . import views

urlpatterns = [
    path('',views.login_view, name='login_view'),
    path('index/',views.index, name= 'index'),
    
 ]
