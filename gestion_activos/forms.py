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
    grupo = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Rol (Grupo)")

    # Nuevos campos para la contraseña
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'nombres', 'apellidos', 'ci', 'grupo', 'password', 'password2']

    def clean_password2(self):
        # Validación para asegurar que las dos contraseñas coinciden
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cd['password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Si estamos editando, hacemos los campos de contraseña opcionales
            self.fields['password'].required = False
            self.fields['password2'].required = False

            # También poblamos los datos del perfil
            if hasattr(self.instance, 'perfil'):
                self.fields['nombres'].initial = self.instance.perfil.nombres
                self.fields['apellidos'].initial = self.instance.perfil.apellidos
                self.fields['ci'].initial = self.instance.perfil.ci

    def save(self, commit=True):
        user = super().save(commit=False)

        # Si se proporcionó una nueva contraseña, la establecemos
        if self.cleaned_data["password"]:
            user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
            # Asignamos el grupo
            user.groups.set([self.cleaned_data['grupo']])

            # Guardamos los datos del Perfil
            user.perfil.nombres = self.cleaned_data['nombres']
            user.perfil.apellidos = self.cleaned_data['apellidos']
            user.perfil.ci = self.cleaned_data['ci']
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