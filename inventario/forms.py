from django import forms
from .models import Producto, Categoria

class ProductoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            if not Categoria.objects.exists():
                self.fields['categoria'].required = False
                self.fields['categoria'].empty_label = "Crear categoría primero"
        except:
            self.fields['categoria'].required = False
            self.fields['categoria'].empty_label = "Error cargando categorías"

    class Meta:  # 👈 ESTE BLOQUE ESTABA MAL UBICADO
        model = Producto
        fields = ['codigo', 'nombre', 'categoria', 'descripcion', 'precio_unitario', 'cantidad', 'stock_minimo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: NB-ACE-001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Notebook Acer Aspire 5'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción...'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Ej: 5'})
        }
        labels = {
            'codigo': 'Código del Producto',
            'nombre': 'Nombre del Producto',
            'categoria': 'Categoría',
            'descripcion': 'Descripción',
            'precio_unitario': 'Precio Unitario (Gs.)',
            'cantidad': 'Cantidad en Stock',
            'stock_minimo': 'Stock Mínimo'
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Computadoras'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Descripción...'})
        }
        labels = {
            'nombre': 'Nombre de la Categoría',
            'descripcion': 'Descripción'
        }


class AgregarStockForm(forms.Form):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        label="Producto",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cantidad = forms.IntegerField(
        min_value=1,
        label="Cantidad a agregar",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )