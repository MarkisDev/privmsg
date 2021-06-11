from django.conf.urls import include
from django.urls import path
from django.contrib import admin

urlpatterns = [
    path('room/', include('chat.urls')),
    path('admin/', admin.site.urls),
    path('msg/', include('msg.urls'))
]