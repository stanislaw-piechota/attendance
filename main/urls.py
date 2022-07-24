from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name="index"),
    path('student/', views.student, name="student"),
    path('success/', views.success, name="success"),
    path('login/', views.teacher_login, name="teacher_login"),
    path('teacher/', views.teacher, name="teacher"),
    path('headmaster/', views.master, name="master"),
    path('s/<str:full_name>/', views.user_s, name="user_s"),
    path('t/<str:full_name>/', views.user_t, name="user_t")
]