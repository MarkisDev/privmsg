from django.shortcuts import render, redirect, reverse


# Landing page
def index(request):
    return render(request, 'home/home.html')

# About page
def about(request):
    return render(request, 'home/about.html')\

# TOS page
def tos(request):
    return render(request, 'home/tos.html')