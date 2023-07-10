from django.urls import path
from . import views

urlpatterns = [
# #     path('',views.login_view, name='login_view'),
    path('login/',views.login_users, name= 'login'),
    path('logut/',views.logout_users, name= 'logout'),
    
  ]
