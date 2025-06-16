# pedidos/forms.py
from django import forms
from .models import Pedido

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = '__all__'
        widgets = {
            'fecha_recepcion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_entrega_estimada': forms.DateInput(attrs={'type': 'date'}),
            'fecha_entrega_real': forms.DateInput(attrs={'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
        }
