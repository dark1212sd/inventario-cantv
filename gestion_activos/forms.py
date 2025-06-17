from django import forms
from .models import Activo, Categoria, Ubicacion
from django.contrib.auth.models import User, Group

class ActivoForm(forms.ModelForm):
    responsable = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Responsable (Usuario)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Activo
        exclude = ['fecha_registro']
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
    grupo = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Rol (Grupo)")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'grupo']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            user.groups.clear()
            user.groups.add(self.cleaned_data['grupo'])
        return user