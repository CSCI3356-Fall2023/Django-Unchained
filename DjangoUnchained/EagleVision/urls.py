from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"), 
    path('profile/', views.user_profile, name='profile'),
    path('change_state/', views.change_state, name='change_state'),
    #path('api/', views.api_endpoint, name='api'),
    path('student/extra_info/', views.student_extra_info, name='student_extra_info'),
    path('admin/extra_info/', views.admin_extra_info, name='admin_extra_info'),
    path('role_selection/', views.role_selection, name='role_selection'),
    path('login', views.login,name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),
    path('courseselection/', views.course_selection, name='courseselect'),
    path('search/', views.search_results, name='search_results'),
    path('filter/', views.filter, name="filter"),
    path('filterRequest/', views.filterRequest, name="filterRequest"),
    path('watchlist/', views.watchlist, name="watchlist"),
    path('add_to_watchlist/', views.add_to_watchlist, name='add_to_watchlist'),
    path('remove_from_watchlist/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('section_selection/<str:id>', views.section_api_endpoint, name='section_selection'),
    path('admin/report/', views.admin_report, name='admin_report'),
    path('admin/report/detailed/<str:course_id>/<int:snapshot_id>/', views.detailed_report, name='detailed_report'),
    path('system_snapshots/', views.list_system_snapshots, name='list_system_snapshots'),
    #path('change_seats/<uuid:section_id>/', views.change_seats, name='change_seats'),
    #path('sort_sections/<str:course_id>/', views.sort_sections, name='sort_sections'),
    path('course_report_filter/', views.course_report_filter, name='course_report_filter'),
]