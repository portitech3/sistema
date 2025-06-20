from django import forms
from .models import Pedido

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'cliente', 'categoria', 'descripcion', 'producto', 'cantidad',
            'estado', 'fecha_recepcion', 'fecha_entrega_estimada', 'fecha_entrega_real'
        ]
        widgets = {
            'cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente'
            }),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada del pedido o requerimientos especiales'
            }),
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Cantidad'
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'fecha_recepcion': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'fecha_entrega_estimada': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'fecha_entrega_real': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
        labels = {
            'cliente': 'Cliente',
            'categoria': 'Categoría',
            'descripcion': 'Descripción del pedido',
            'producto': 'Producto/Trofeo',
            'cantidad': 'Cantidad',
            'estado': 'Estado del pedido',
            'fecha_recepcion': 'Fecha de recepción',
            'fecha_entrega_estimada': 'Fecha de entrega estimada',
            'fecha_entrega_real': 'Fecha de entrega real',
        }
        help_texts = {
            'estado': 'Borrador: No afecta inventario. Confirmado: Descuenta inventario.',
            'cantidad': 'Cantidad de trofeos a fabricar',
            'fecha_entrega_estimada': 'Fecha comprometida con el cliente',
            'fecha_entrega_real': 'Completar cuando se entregue efectivamente',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si es un pedido nuevo, establecer estado por defecto
        if not self.instance.pk:
            self.fields['estado'].initial = 'borrador'
        
        # Hacer que algunos campos sean opcionales en ciertos casos
        if self.instance.pk and self.instance.estado in ['borrador']:
            self.fields['fecha_entrega_real'].required = False
        
        # Agregar información de stock disponible al campo producto
        if 'producto' in self.fields:
            queryset = self.fields['producto'].queryset
            choices = [(None, '---------')]
            for producto in queryset:
                stock_info = f" (Stock: {producto.cantidad})" if hasattr(producto, 'cantidad') else ""
                choices.append((producto.pk, f"{producto.nombre}{stock_info}"))
            self.fields['producto'].choices = choices

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        estado = cleaned_data.get('estado')
        
        # Validar stock solo si se va a confirmar el pedido
        if producto and cantidad and estado in ['confirmado', 'produccion', 'terminacion', 'terminado', 'entregado']:
            # Si es un pedido existente, verificar si ya tiene inventario descontado
            if self.instance.pk:
                pedido_actual = Pedido.objects.get(pk=self.instance.pk)
                # Si ya tenía inventario descontado, ajustar la validación
                if pedido_actual.inventario_descontado:
                    stock_disponible = producto.cantidad + pedido_actual.cantidad
                else:
                    stock_disponible = producto.cantidad
            else:
                stock_disponible = producto.cantidad
            
            if cantidad > stock_disponible:
                raise forms.ValidationError(
                    f'Stock insuficiente para {producto.nombre}. '
                    f'Disponible: {stock_disponible}, Requerido: {cantidad}'
                )
        
        return cleaned_data

    def clean_fecha_entrega_estimada(self):
        fecha = self.cleaned_data.get('fecha_entrega_estimada')
        fecha_recepcion = self.cleaned_data.get('fecha_recepcion')
        
        if fecha and fecha_recepcion and fecha < fecha_recepcion:
            raise forms.ValidationError(
                'La fecha de entrega estimada no puede ser anterior a la fecha de recepción.'
            )
        
        return fecha

    def clean_fecha_entrega_real(self):
        fecha = self.cleaned_data.get('fecha_entrega_real')
        fecha_recepcion = self.cleaned_data.get('fecha_recepcion')
        
        if fecha and fecha_recepcion and fecha < fecha_recepcion:
            raise forms.ValidationError(
                'La fecha de entrega real no puede ser anterior a la fecha de recepción.'
            )
        
        return fecha


class FiltrosPedidoForm(forms.Form):
    """Formulario para filtros en la lista de pedidos"""
    cliente = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por cliente...'
        })
    )
    
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los estados')] + Pedido.ESTADOS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='Desde'
    )
    
    hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='Hasta'
    )