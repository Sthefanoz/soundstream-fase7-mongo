"""
Formularios para registro de Usuario y CRUD de Playlist (BD real Fase 3).
"""

from django import forms
from django.utils import timezone

from .models import Usuario, Playlist


class RegistroForm(forms.ModelForm):
    password = forms.CharField(label='Contrasena', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repite la contrasena', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ('primer_nombre', 'primer_apellido', 'email', 'pais')
        labels = {
            'primer_nombre': 'Nombre',
            'primer_apellido': 'Apellido',
            'email': 'Correo electronico',
            'pais': 'Pais',
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con ese correo.')
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password2'):
            self.add_error('password2', 'Las contrasenas no coinciden.')
        return cleaned

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.password = self.cleaned_data['password']
        usuario.estado_cuenta = 'Activo'
        usuario.rol = 'usuario'
        # fechaRegistro se guarda como texto ISO (asi estan los documentos).
        usuario.fecha_registro = timezone.localdate().isoformat()
        if commit:
            usuario.save()
        return usuario


class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ('nombre', 'descripcion', 'tipo_visibilidad')
        labels = {
            'nombre': 'Nombre de la playlist',
            'descripcion': 'Descripcion',
            'tipo_visibilidad': 'Visibilidad',
        }
