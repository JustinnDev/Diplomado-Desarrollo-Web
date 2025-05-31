from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('manage_staff/', views.manage_staff, name='manage_staff'),
    path('manage_staff/<int:user_id>/', views.manage_staff, name='manage_staff_detail'),
]
