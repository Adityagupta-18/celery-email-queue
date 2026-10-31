from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('mails-sent/',views.mail_sent,name='mail_sender'),
    path('task-status/<str:task_id>/', views.task_status, name='task_status'),
]