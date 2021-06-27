from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django import urls
from django.contrib import messages
import hashlib
import pymongo
import string
import random
import datetime
import random
import json


with open('chat/config.json') as f:
    contents = json.load(f)
    if contents["DATABASE"]:
        # If database_url configured in config.json
        db_url = contents['DATABASE_URL'] 
        db_client = pymongo.MongoClient(db_url)
        # Selecting database
        db = db_client['privmsg']
        col = db["rooms"]

# Function to handle the form to create room
def index(request):
    # Handling form request
    if request.method == 'POST':
        if request.POST.get('room_name') is not None and request.POST.get('room_name').strip() == '':
            messages.error(request, 'No room error!')
            return render(request, 'chat/index.html', {'error': True})
        elif request.POST.get('room_name'):
            return redirect(reverse('chat:room', kwargs={"room_name": request.POST.get('room_name')}))
        # Password was not set
        if not request.POST.get('password'):
            messages.error(request, 'No password error!')
            return render(request, 'chat/index.html', {'error': True})
        # Username was not set
        elif not request.POST.get('username'):
            messages.error(request, 'No username error!')
            return render(request, 'chat/index.html', {'error': True})
        # Everything set, adding to db then sending to a burner room!
        else:
            # Generating a random room name and inserting to db
            room_name = gen_room()
            # Hashing the password
            room_pass = hashlib.sha256(request.POST.get('password').encode()).hexdigest()
            data = {'room_name':room_name, 'password':room_pass, 'created_time': datetime.datetime.utcnow(), 'messages':[], 'connected_clients':0}
            col.insert(data)
            # Setting a session with room_name so HOPEFULLY no one fakes it
            request.session['room_name'] = room_name
            request.session['username'] = request.POST.get('username')
            # Temp session variable to grant access without auth
            request.session['admin_bypass'] = True
            return redirect(reverse('chat:room', kwargs={"room_name": room_name}))
    # Handling GET request
    else:
        return render(request, 'chat/index.html', {'error': False})

# Function to render room page, rest of it is handled by websocket connection!
def room(request, room_name):
    # Colors list for the user
    colors = ['#2626be', '#ad011d', '#900174', '#09578a', '#098a4c', '#49456f', '#314645', '#087e78', '#653a24', '#556106']
    random.shuffle(colors)
    color = random.choice(colors)
    # Handling GET request:
    if request.method == 'GET':
        # Granting page access if user created the room and was redirected
        if 'room_name' in request.session and request.session['room_name'] == room_name:
            # Deleting variable so he will have to relogin next time
            username = request.session['username']
            del request.session['room_name'] 
            del request.session['username'] 
            return render(request, 'chat/room.html', {'room_name': room_name, 'username':username, 'color':color})
        else:
            room = col.find_one({'room_name':room_name}, {'_id':0, 'created_at':0, 'messages':0})
            if room is None:
                # return redirect(reverse('chat:home'))
                messages.error(request, 'Room does not exist')
                return redirect(reverse('chat:home'))
            return render(request, 'chat/index.html', {'error': False, 'join': True})
    # User submitted form to login, authenticating him
    elif request.method == 'POST':
        if request.POST.get('username').strip() == '':
            messages.error(request, 'No username error!')
            return render(request, 'chat/index.html', {'error': False, 'join': True})
        # Checking if it's not a spam post request 
        if not request.POST.get('password'):
            messages.error(request, 'No password error!')
            return render(request, 'chat/index.html', {'error': False, 'join': True})
        # Checking room exists in db
        room = col.find_one({'room_name':room_name}, {'_id':0, 'created_at':0, 'messages':0})
        if room is None:
            messages.error(request, 'Room does not exist')
            return redirect(reverse('chat:home'))
        else:
            # Checking if password is same
            room_pass = hashlib.sha256(request.POST.get('password').encode()).hexdigest()
            if room_pass == room['password']:
                return render(request, 'chat/room.html', {'room_name': room_name, 'username': request.POST.get('username'), 'color':color})
            else:
                messages.error(request, 'Room password wrong!')
                return render(request, 'chat/index.html', {'error': False, 'join': True})
            

# Function to generate a random room name
def gen_room(length=random.randint(5, 7)):
    # List of strings that can be used for a password
    text = f"{string.ascii_letters}{string.digits}"
    text = list(text)
    # Shuffling the text
    random.shuffle(text)
    # Returning a randomly chosen password
    room_name =  ''.join(random.choices(text, k=length))
    # Checking if room name exists
    db_unique = db['data'].find_one({'room_name':room_name}, {'_id':0, 'created_at':0, 'messages':0})
    # Exists, so making a recursive call
    if db_unique:
        gen_room()
    else:
        return room_name
