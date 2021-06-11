from django.urls import path
from . import views

app_name = 'msg'
urlpatterns = [
    path('', views.create_msg, name='home'),
    path('<str:msg_name>/', views.read, name='read'),
]