from django import forms
from .models import Producto, Categoria

class ProductoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer categoria opcional temporalmente si no hay categorías
        try:
            if not Categoria.objects.exists():
                self.fields['categoria'].required = False
                self.fields['categoria'].empty_label = "Crear categoría primero"
        except:
            self.fields['categoria'].required = False
            self.fields['categoria'].empty_label = "Error cargando categorías"
    
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'categoria', 'descripcion', 'precio_unitario', 'cantidad']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: NB-ACE-001'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Notebook Acer Aspire 5'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada del producto...'
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            })
        }
        labels = {
            'codigo': 'Código del Producto',
            'nombre': 'Nombre del Producto',
            'categoria': 'Categoría',
            'descripcion': 'Descripción',
            'precio_unitario': 'Precio Unitario (Gs.)',
            'cantidad': 'Cantidad en Stock'
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Computadoras'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripción de la categoría...'
            })
        }
        labels = {
            'nombre': 'Nombre de la Categoría',
            'descripcion': 'Descripción'
        }