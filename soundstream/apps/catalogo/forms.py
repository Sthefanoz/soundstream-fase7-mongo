"""
Formularios del panel de administracion para el CRUD del catalogo (MongoDB).

La discografica va embebida en el artista (un solo campo de texto con su
nombre). El artista de un album y el album de una cancion se eligen por su id.
"""

from django import forms

from .models import Artista, Album, Cancion


class ArtistaForm(forms.ModelForm):
    # La discografica es un documento embebido; en el formulario basta su nombre.
    discografica_nombre = forms.CharField(
        label='Discografica', required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Sello discografico'}))

    class Meta:
        model = Artista
        fields = ('nombre', 'biografia', 'foto')
        labels = {
            'nombre': 'Nombre artistico',
            'biografia': 'Biografia',
            'foto': 'URL de la foto',
        }
        widgets = {
            'biografia': forms.Textarea(attrs={'rows': 4}),
            'foto': forms.TextInput(attrs={'placeholder': 'https://...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Precarga el nombre de la discografica embebida al editar.
        if self.instance and self.instance.pk and self.instance.discografica:
            self.fields['discografica_nombre'].initial = self.instance.discografica.nombre


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ('titulo', 'fecha_lanzamiento', 'portada', 'artista')
        labels = {
            'titulo': 'Titulo',
            'fecha_lanzamiento': 'Fecha de lanzamiento (AAAA-MM-DD)',
            'portada': 'URL de la portada',
            'artista': 'Artista',
        }
        widgets = {
            'fecha_lanzamiento': forms.TextInput(attrs={'placeholder': '2024-01-31'}),
            'portada': forms.TextInput(attrs={'placeholder': 'https://...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['artista'].required = True
        self.fields['artista'].queryset = Artista.objects.all()


class CancionForm(forms.ModelForm):
    CALIDADES = [('320kbps', '320 kbps'), ('FLAC', 'FLAC'), ('128kbps', '128 kbps')]

    calidad_audio = forms.ChoiceField(choices=CALIDADES, label='Calidad de audio')

    class Meta:
        model = Cancion
        fields = ('titulo', 'duracion', 'calidad_audio', 'album')
        labels = {
            'titulo': 'Titulo',
            'duracion': 'Duracion (HH:MM:SS)',
            'album': 'Album',
        }
        widgets = {
            'duracion': forms.TextInput(attrs={'placeholder': '00:03:45'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['album'].required = True
        self.fields['album'].queryset = Album.objects.all()
