from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('university/<int:pk>/', views.university_detail_view, name='university_detail'),
    path('university/<int:pk>/add/', views.add_university_view, name='add_university'),
    path('university/<int:pk>/remove/', views.remove_university_view, name='remove_university'),
    path('my-universities/', views.my_universities_view, name='my_universities'),
    # Reviews
    path('university/<int:pk>/review/', views.add_review_view, name='add_review'),
    path('university/<int:pk>/review/<int:review_pk>/edit/', views.edit_review_view, name='edit_review'),
    path('university/<int:pk>/review/<int:review_pk>/delete/', views.delete_review_view, name='delete_review'),
    # Rank Yourself
    path('rank/', views.rank_yourself_view, name='rank_yourself'),
    path('rank/save/', views.save_ranking, name='save_ranking'),
]
