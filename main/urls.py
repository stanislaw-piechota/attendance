from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('student/', views.student, name="student"),
    path('success/', views.success, name="success"),
    path('login/', views.teacher_login, name="teacher_login"),
    path('teacher/', views.teacher, name="teacher"),
    path('headmaster/', views.master, name="master")
]