from django.shortcuts import render, redirect, reverse


# Landing page
def index(request):
    return render(request, 'home/home.html')