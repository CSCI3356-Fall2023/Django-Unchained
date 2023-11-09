from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('logout/', views.logout_view, name='logout'),
    # path('correctlogin/', views.login_view, name='correctlogin'), 
    path('register/', views.register, name='register'),
    path('register/student/', views.student_register, name='student_register'),
    path('register/admin/', views.admin_register, name='admin_register'),
    path('profile/', views.user_profile, name='profile'),
    path('change_state/', views.change_state, name='change_state'),
    path('courseselection/', views.course_selection, name='courseselect'),
    path('api/', views.api_endpoint, name='api'),
    path('student/extra_info/', views.student_extra_info, name='student_extra_info'),
    path('admin/extra_info/', views.admin_extra_info, name='admin_extra_info'),
    path('role_selection/', views.role_selection, name='role_selection'),
    path("", views.index, name="index"),
    path('login', views.login,name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),
    path('courseselection/', views.course_selection, name='courseselect')
    #path('courses/', views.display_courses, name='display_courses'),
]