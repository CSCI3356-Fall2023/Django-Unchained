from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home_view, name='home'), 
    #path('login', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('correctlogin/', views.login_view, name='correctlogin'), 
    path('register/', views.register, name='register'),
    path('register/student/', views.student_register, name='student_register'),
    path('register/admin/', views.admin_register, name='admin_register'),
    path('profile/', views.user_profile, name='profile'),
    path('change_state/', views.change_state, name='change_state'),
    path('courseselection/', views.course_selection, name='courseselect')
]