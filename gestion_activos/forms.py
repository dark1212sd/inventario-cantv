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
        queryset=User.objects.all().order_by('username'),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bucle para añadir la clase 'form-control' a todos los campos
        for field_name, field in self.fields.items():
            # A los campos de tipo 'select' les ponemos la clase 'form-select'
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        # Definimos los widgets aquí para añadir las clases de Bootstrap
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        # Personalizamos las etiquetas para que sean más claras
        labels = {
            'nombre': 'Nombre de la Categoría',
            'descripcion': 'Descripción (Opcional)',
        }

class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = ['nombre', 'descripcion']
        # Definimos los widgets para añadir las clases de Bootstrap
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        # Personalizamos las etiquetas para que sean más claras
        labels = {
            'nombre': 'Nombre de la Ubicación',
            'descripcion': 'Descripción (Opcional)',
        }
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
    email = forms.EmailField(label="Correo Electrónico", required=True)
    nombres = forms.CharField(label="Nombres", required=False)
    apellidos = forms.CharField(label="Apellidos", required=False)
    ci = forms.CharField(label="Cédula (CI)", required=False)
    telefono_contacto = forms.CharField(label="Teléfono Principal", required=False)
    grupo = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Rol (Grupo)")
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        required=False,
        help_text="Debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número."
    )

    class Meta:
        model = User
        # Asegúrate de que todos los campos estén listados aquí
        fields = ['username', 'email', 'nombres', 'apellidos', 'ci', 'telefono_contacto', 'grupo', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es un usuario nuevo, la contraseña es obligatoria
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

    # --- VALIDACIONES ---
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean_ci(self):
        ci = self.cleaned_data.get('ci')
        if ci:
            query = Perfil.objects.filter(ci=ci)
            if self.instance and self.instance.pk:
                query = query.exclude(user=self.instance)
            if query.exists():
                raise forms.ValidationError('Este número de cédula ya está en uso.')
        return ci

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.instance.pk and not password:
            raise forms.ValidationError("La contraseña es obligatoria para nuevos usuarios.")
        if password:
            if len(password) < 8: raise forms.ValidationError("Debe tener al menos 8 caracteres.")
            if not re.search(r'[A-Z]', password): raise forms.ValidationError("Debe contener al menos una mayúscula.")
            if not re.search(r'[a-z]', password): raise forms.ValidationError("Debe contener al menos una minúscula.")
            if not re.search(r'[0-9]', password): raise forms.ValidationError("Debe contener al menos un número.")
        return password

    def save(self, commit=True):
        # ... (La lógica de guardado que ya teníamos funciona bien con esto)
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