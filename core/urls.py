from django.urls import path
from . import views

urlpatterns = [
    path('tasks/', views.task_list, name='task_list'),
    path('tasks_create/', views.task_create, name='task_create'),
    path('task/<slug:slug>/', views.task_detail, name='task_detail'),
    path('submission/<int:pk>/', views.submission_detail, name='submission_detail'),
     path('author/<str:prepod>/', views.author_tasks_view, name='author_tasks'),
]
