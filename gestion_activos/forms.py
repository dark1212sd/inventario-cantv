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
    """
    Formulario completo para que un Admin cree o edite usuarios,
    con todas las validaciones robustas.
    """
    # Campos que no están en el modelo User, los definimos explícitamente.
    nombres = forms.CharField(label="Nombres", required=False)
    apellidos = forms.CharField(label="Apellidos", required=False)
    ci = forms.CharField(label="Cédula (CI)", required=False)
    telefono_contacto = forms.CharField(label="Teléfono Principal", required=False)
    grupo = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Rol (Grupo)")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'nombres', 'apellidos', 'ci', 'telefono_contacto', 'grupo', 'password',
                  'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando un usuario existente (self.instance.pk tiene un valor)
        if self.instance and self.instance.pk:
            # Poblamos los campos del perfil con los datos guardados
            if hasattr(self.instance, 'perfil'):
                self.fields['nombres'].initial = self.instance.perfil.nombres
                self.fields['apellidos'].initial = self.instance.perfil.apellidos
                self.fields['ci'].initial = self.instance.perfil.ci
                self.fields['telefono_contacto'].initial = self.instance.perfil.telefono_contacto

            # Poblamos el grupo actual del usuario
            self.fields['grupo'].initial = self.instance.groups.first()
        else:
            # Si estamos creando un usuario nuevo, la contraseña es obligatoria
            self.fields['password'].required = True
            self.fields['password2'].required = True

    # --- VALIDACIONES PERSONALIZADAS ---

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Excluimos el propio usuario de la búsqueda para permitir guardar sin cambios
        if User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def clean_ci(self):
        ci = self.cleaned_data.get('ci')
        if ci:  # Solo validamos si se ingresó algo
            query = Perfil.objects.filter(ci=ci)
            # Al editar, excluimos al propio usuario de la búsqueda de duplicados
            if self.instance and self.instance.pk:
                query = query.exclude(user=self.instance)
            if query.exists():
                raise forms.ValidationError('Ya existe un usuario con este número de cédula.')
        return ci

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        # Si se ingresó una contraseña, ambas deben coincidir
        if password and password != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)

        if commit:
            user.save()
            user.groups.set([self.cleaned_data['grupo']])
            # Usamos hasattr para el caso de que el perfil no se haya creado aún (aunque la señal debería hacerlo)
            if not hasattr(user, 'perfil'):
                Perfil.objects.create(user=user)
            # Actualizamos los datos del perfil
            user.perfil.nombres = self.cleaned_data.get('nombres', '')
            user.perfil.apellidos = self.cleaned_data.get('apellidos', '')
            user.perfil.ci = self.cleaned_data.get('ci', '')
            user.perfil.telefono_contacto = self.cleaned_data.get('telefono_contacto', '')
            user.perfil.save()

        return user