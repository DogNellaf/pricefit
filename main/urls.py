from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Requests
    path('requests/', views.request_list, name='request_list'),
    path('requests/new/', views.request_create, name='request_create'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('requests/<int:pk>/edit/', views.request_edit, name='request_edit'),
    path('requests/<int:pk>/delete/', views.request_delete, name='request_delete'),
    path('requests/<int:pk>/analyze/', views.request_analyze, name='request_analyze'),
    # Target groups
    path('groups/', views.target_group_list, name='target_group_list'),
    path('groups/new/', views.target_group_create, name='target_group_create'),
    path('groups/<int:pk>/edit/', views.target_group_edit, name='target_group_edit'),
    path('groups/<int:pk>/delete/', views.target_group_delete, name='target_group_delete'),
]
