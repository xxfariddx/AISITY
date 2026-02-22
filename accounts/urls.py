from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('role-select/', views.role_select_view, name='role_select'),
    path('study-location/', views.study_location_view, name='study_location'),
    path('profile/', views.profile_view, name='profile'),
]
