from django import forms
from .models import Activo, Categoria, Ubicacion
from django.contrib.auth.models import User, Group
from .models import Perfil
import re

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
        model = Categoria
        fields = ['nombre', 'descripcion']


class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = ['nombre', 'descripcion']

class UsuarioForm(forms.ModelForm):
    # Campos del modelo User y Perfil
    email = forms.EmailField(label="Correo Electrónico", required=True)
    nombres = forms.CharField(label="Nombres", required=True)
    apellidos = forms.CharField(label="Apellidos", required=True)
    ci = forms.CharField(label="Cédula (CI)", required=True)
    telefono_contacto = forms.CharField(label="Teléfono Principal", required=True)
    grupo = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Rol (Grupo)")

    # Campos para la contraseña con su confirmación
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'nombres', 'apellidos', 'ci', 'telefono_contacto', 'grupo', 'password', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando un usuario existente...
        if self.instance and self.instance.pk:
            # Poblamos los campos del perfil con los datos existentes
            if hasattr(self.instance, 'perfil'):
                self.fields['nombres'].initial = self.instance.perfil.nombres
                self.fields['apellidos'].initial = self.instance.perfil.apellidos
                self.fields['ci'].initial = self.instance.perfil.ci
                self.fields['telefono_contacto'].initial = self.instance.perfil.telefono_contacto

            # Poblamos el grupo actual
            self.fields['grupo'].initial = self.instance.groups.first()
        else:
            # Si estamos creando, la contraseña es obligatoria
            self.fields['password'].required = True
            self.fields['password2'].required = True

    # --- VALIDACIONES PERSONALIZADAS ---

    def clean_username(self):
        """Valida que el nombre de usuario no esté ya en uso."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso. Por favor, elige otro.')
        return username

    def clean_ci(self):
        """Valida que la cédula no esté ya en uso, corrigiendo el error al crear."""
        ci = self.cleaned_data.get('ci')
        if not ci:
            return ci

        query = Perfil.objects.filter(ci=ci)
        # Si estamos editando (self.instance.pk tiene un valor), excluimos al usuario actual.
        if self.instance and self.instance.pk:
            query = query.exclude(user=self.instance)

        if query.exists():
            raise forms.ValidationError('Ya existe un usuario con este número de cédula.')
        return ci

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

    def clean_password2(self):
        """Valida que las dos contraseñas coincidan."""
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        # Solo validamos si se ha ingresado algo en el primer campo de contraseña
        if password and password != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        # Guardamos el objeto User, pero sin commit para manejar la contraseña
        user = super().save(commit=False)

        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)

        if commit:
            user.save()
            # Asignamos el grupo
            user.groups.set([self.cleaned_data['grupo']])

            # Actualizamos o creamos el perfil
            # Usamos hasattr para el caso de que el perfil no exista (aunque la señal debería crearlo)
            if not hasattr(user, 'perfil'):
                Perfil.objects.create(user=user)

            user.perfil.nombres = self.cleaned_data['nombres']
            user.perfil.apellidos = self.cleaned_data['apellidos']
            user.perfil.ci = self.cleaned_data['ci']
            user.perfil.telefono_contacto = self.cleaned_data['telefono_contacto']
            user.perfil.save()

        return user

class UsuarioActivoForm(forms.ModelForm):
    class Meta:
        model = Activo
        # Excluimos los campos que un usuario normal no debe cambiar
        exclude = ['responsable', 'codigo', 'fecha_registro']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

# --- NUEVO: AÑADIMOS EL FORMULARIO QUE FALTABA ---
class LoginForm(forms.Form):
    """
    Formulario para el inicio de sesión de usuarios.
    """
    username = forms.CharField(
        label="Nombre de Usuario",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su usuario'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        })
    )

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['nombres', 'apellidos', 'ci', 'telefono_contacto', 'telefono_alterno', 'fecha_nacimiento']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control', 'placeholder': f'Ingrese su {field.label.lower()}'})
