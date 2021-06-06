from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django import urls


# Function to handle the form to create room
def index(request):
    if request.method == 'POST':
        request.session['password_lol'] = request.POST.get('password')
        return redirect(reverse('chat:room', kwargs={"room_name": request.POST.get('roomname')}))
    else:
        return render(request, 'chat/index.html')


def room(request, room_name):
    if 'password_lol' not in request.session:
        return HttpResponse("Madarchod")
    else:
        return render(request, 'chat/room.html', {
            'room_name': room_name
        })
