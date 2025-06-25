from django import forms
from .models import Activo, Categoria, Ubicacion
from django.contrib.auth.models import User, Group
from .models import Perfil
import re

from django import forms
from django.contrib.auth.models import User, Group
from .models import Activo, Categoria, Ubicacion, Perfil
import re


# ==============================================================================
# FORMULARIO DE LOGIN
# ==============================================================================
class LoginForm(forms.Form):
    """Formulario para el inicio de sesión de usuarios."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su contraseña'})
    )


# ==============================================================================
# FORMULARIOS PARA MODELOS CRUD (Activo, Categoria, Ubicacion)
# ==============================================================================
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
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 3})}


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']


class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = ['nombre', 'descripcion']


# ==============================================================================
# FORMULARIOS ESPECÍFICOS PARA EL ROL "USUARIO"
# ==============================================================================
class UsuarioActivoForm(forms.ModelForm):
    """Formulario restringido para que un usuario edite su propio activo."""

    class Meta:
        model = Activo
        exclude = ['responsable', 'codigo', 'fecha_registro']
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 3})}


class PerfilForm(forms.ModelForm):
    """Formulario para que los usuarios editen su propia información de perfil."""

    class Meta:
        model = Perfil
        fields = ['nombres', 'apellidos', 'ci', 'telefono_contacto', 'telefono_alterno', 'fecha_nacimiento']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_telefono_contacto(self):
        """Valida que el teléfono tenga un formato venezolano válido."""
        telefono = self.cleaned_data.get('telefono_contacto')
        if telefono:
            telefono_limpio = re.sub(r'\D', '', telefono)
            patron = re.compile(r'^(0412|0414|0424|0416|0426)\d{7}$')
            if not patron.match(telefono_limpio):
                raise forms.ValidationError("Formato inválido. Usa un prefijo válido (0412, etc.) y 11 dígitos.")
            return telefono_limpio
        return telefono


# ==============================================================================
# FORMULARIO DE GESTIÓN DE USUARIOS (Para Admins) - VERSIÓN FINAL
# ==============================================================================

class UsuarioForm(forms.ModelForm):
    # Definimos los campos para tener control total
    email = forms.EmailField(label="Correo Electrónico", required=True)
    nombres = forms.CharField(label="Nombres", required=False)
    apellidos = forms.CharField(label="Apellidos", required=False)
    ci = forms.CharField(label="Cédula (CI)", required=False)
    telefono_contacto = forms.CharField(label="Teléfono Principal", required=False)
    grupo = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Rol (Grupo)")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'nombres', 'apellidos', 'ci', 'telefono_contacto', 'grupo', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos creando un usuario nuevo, la contraseña es obligatoria
        if not self.instance.pk:
            self.fields['password'].required = True

        # Si estamos editando, poblamos los campos del perfil
        if self.instance and self.instance.pk:
            if hasattr(self.instance, 'perfil'):
                self.fields['nombres'].initial = self.instance.perfil.nombres
                self.fields['apellidos'].initial = self.instance.perfil.apellidos
                self.fields['ci'].initial = self.instance.perfil.ci
                self.fields['telefono_contacto'].initial = self.instance.perfil.telefono_contacto
            self.fields['grupo'].initial = self.instance.groups.first()

    def clean_password(self):
        """Validación de contraseña robusta."""
        password = self.cleaned_data.get('password')
        # La contraseña solo es obligatoria si estamos creando un usuario nuevo
        if not self.instance.pk and not password:
            raise forms.ValidationError("La contraseña es obligatoria para nuevos usuarios.")

        if password:  # Aplicar validaciones solo si se proveyó una contraseña
            if len(password) < 8:
                raise forms.ValidationError("Debe tener al menos 8 caracteres.")
            if not re.search(r'[A-Z]', password):
                raise forms.ValidationError("Debe contener al menos una mayúscula.")
            if not re.search(r'[a-z]', password):
                raise forms.ValidationError("Debe contener al menos una minúscula.")
            if not re.search(r'[0-9]', password):
                raise forms.ValidationError("Debe contener al menos un número.")
        return password

    # ... (El resto de tus validaciones como clean_username y clean_ci se quedan igual) ...

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
            user.groups.set([self.cleaned_data['grupo']])
            perfil, created = Perfil.objects.get_or_create(user=user)
            perfil.nombres = self.cleaned_data.get('nombres', '')
            perfil.apellidos = self.cleaned_data.get('apellidos', '')
            perfil.ci = self.cleaned_data.get('ci', '')
            perfil.telefono_contacto = self.cleaned_data.get('telefono_contacto', '')
            perfil.save()
        return user