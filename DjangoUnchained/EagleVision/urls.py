from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'), 
    path('', views.forgot, name='forgotPassword'), 
    path('', views.signup, name='signUp'),
    path('', views.signin, name='signin')
]