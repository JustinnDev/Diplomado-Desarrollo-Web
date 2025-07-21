from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'landing/index.html')

def material1(request):
    return render(request, 'landing/material1.html')

def material2(request):
    return render(request, 'landing/material2.html')