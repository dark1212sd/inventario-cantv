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
    # Campos del modelo User
    username = forms.CharField(label="Nombre de Usuario", required=True)
    email = forms.EmailField(label="Correo Electrónico", required=False)
    grupo = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Rol (Grupo)")

    # Nuevos campos del modelo Perfil
    nombres = forms.CharField(label="Nombres", required=False)
    apellidos = forms.CharField(label="Apellidos", required=False)
    ci = forms.CharField(label="Cédula (CI)", required=False)
    telefono_contacto = forms.CharField(label="Teléfono Principal", required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'grupo', 'nombres', 'apellidos', 'ci', 'telefono_contacto']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Si estamos editando, poblamos los campos del perfil
            self.fields['grupo'].initial = self.instance.groups.first()
            if hasattr(self.instance, 'perfil'):
                self.fields['nombres'].initial = self.instance.perfil.nombres
                self.fields['apellidos'].initial = self.instance.perfil.apellidos
                self.fields['ci'].initial = self.instance.perfil.ci
                self.fields['telefono_contacto'].initial = self.instance.perfil.telefono_contacto

            # Hacemos el username de solo lectura al editar
            self.fields['username'].widget.attrs['readonly'] = True

    def save(self, commit=True):
        # Guardamos el objeto User
        user = super().save(commit=False)

        # Si es un usuario nuevo, establecemos una contraseña por defecto (ej: la cédula)
        if not self.instance.pk:
            password = self.cleaned_data.get('ci', 'password123')  # Usamos la cédula o un password por defecto
            user.set_password(password)

        if commit:
            user.save()

            # Asignamos el grupo
            user.groups.clear()
            user.groups.add(self.cleaned_data['grupo'])

            # Guardamos los datos del Perfil
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

    # --- NUEVA FUNCIÓN DE VALIDACIÓN ---
    def clean_telefono_contacto(self):
        telefono = self.cleaned_data.get('telefono_contacto')
        if telefono:
            # Elimina espacios o guiones
            telefono_limpio = re.sub(r'\D', '', telefono)

            # Patrón para prefijos válidos y longitud total de 11 dígitos
            patron = re.compile(r'^(0412|0414|0424|0416|0426)\d{7}$')

            if not patron.match(telefono_limpio):
                raise forms.ValidationError(
                    "Por favor, ingrese un número de teléfono venezolano válido (ej: 04141234567).")

            return telefono_limpio
        return telefono