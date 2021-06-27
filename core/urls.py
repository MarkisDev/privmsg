from django.conf.urls import include
from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home'),
    path('about', views.about, name='about'),
    path('tos', views.tos, name='tos'),
    path('room/', include('chat.urls')),
    path('msg/', include('msg.urls'))
]