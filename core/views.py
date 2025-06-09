
from django.shortcuts import render

def inicio(request):
    return render(request, 'inicio.html')  # Busca inicio.html en /templates
