from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'), 
    path('forgotpassword/', views.forgot, name='forgotPassword'), 
    path('register/', views.register, name='register'),
    path('register/student/', views.student_register, name='student_register'),
    path('register/admin/', views.admin_register, name='admin_register'),
    path('profile/', views.user_profile, name='profile'),
    path('change_state/', views.change_state, name='change_state'),
    path('', views.logout, name='logout'), 
]