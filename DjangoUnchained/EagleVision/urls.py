from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'), 
    path('register/', views.register, name='register'),
    path('register/student/', views.student_register, name='student_register'),
    path('register/admin/', views.admin_register, name='admin_register'),
]