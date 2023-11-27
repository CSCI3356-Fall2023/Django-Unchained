from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"), 
    path('profile/', views.user_profile, name='profile'),
    path('change_state/', views.change_state, name='change_state'),
    path('api/', views.api_endpoint, name='api'),
    path('student/extra_info/', views.student_extra_info, name='student_extra_info'),
    path('admin/extra_info/', views.admin_extra_info, name='admin_extra_info'),
    path('role_selection/', views.role_selection, name='role_selection'),
    path("", views.index, name="index"),
    path('login', views.login,name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),
    path('courseselection/', views.course_selection, name='courseselect'),
    path('search_results/', views.search_results, name='search_results'),
    path('filter/', views.filter, name="filter"),
    path('filterRequest/', views.filterRequest, name="filterRequest"),
    path('watchlist/', views.watchlist, name="watchlist"),
    path('add_to_watchlist/', views.add_to_watchlist, name='add_to_watchlist'),
    path('remove_from_watchlist/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('section_selection/<str:courseName>', views.section_api_endpoint, name='section_selection'),
]