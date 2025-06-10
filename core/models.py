from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    TIPO_CHOICES = [
        ('admin', 'Administrador'),
        ('autor', 'Autor'),
        ('vendedor', 'Vendedor'),
        ('cliente', 'Cliente'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='cliente')
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
