from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'), 
    path('', views.forgot, name='forgotPassword'), 
    path('', views.register, name='register'),
    path('', views.student_register, name='studentRegister'), 
    path('', views.admin_register, name='adminRegister')
]