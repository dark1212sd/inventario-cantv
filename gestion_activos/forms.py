from django import forms
from .models import Activo, Categoria, Ubicacion
from django.contrib.auth.models import User, Group

class ActivoForm(forms.ModelForm):
    class Meta:
        model = Activo
        exclude = ['fecha_registro']  # No se muestra en el formulario
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model  = Categoria
        fields = ['nombre', 'descripcion']

class UbicacionForm(forms.ModelForm):
    class Meta:
        model  = Ubicacion
        fields = ['nombre', 'descripcion']


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    grupo = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label='Grupo')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

