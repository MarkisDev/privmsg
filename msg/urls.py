from django.urls import path
from . import views

app_name = 'msg'
urlpatterns = [
    path('', views.index, name='home'),
    path('<str:msg_name>/', views.msg, name='msg'),
]