from django import forms
from .models import EventosSociales, ConsultasSociales, Reclamo
from users.models import Area, SubArea

class EventoSocialForm(forms.ModelForm):
    class Meta:
        model = EventosSociales
        # Sacamos 'activo' de aquí para que no sea visible ni editable
        fields = ['titulo', 'descripcion', 'lugar', 'fecha_hora', 'imagen']
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Boda en el Prado o Festival de Verano'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe los detalles del evento...'
            }),
            'lugar': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección o nombre del salón'
            }),
            'fecha_hora': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'titulo': 'Título del Evento',
            'descripcion': 'Descripción Detallada',
            'lugar': 'Ubicación / Lugar',
            'fecha_hora': 'Fecha y Hora del Evento',
            'imagen': 'Imagen Promocional',
        }

    def __init__(self, *args, **kwargs):
        super(EventoSocialForm, self).__init__(*args, **kwargs)
        # Formateo de fecha para edición (necesario para el input datetime-local)
        if self.instance and self.instance.fecha_hora:
            self.initial['fecha_hora'] = self.instance.fecha_hora.strftime('%Y-%m-%dT%H:%M')


class ConsultaSocialForm(forms.ModelForm):
    area_destino = forms.ModelChoiceField(
        queryset=Area.objects.all(),
        empty_label="Seleccione el área municipal",
        label="¿A qué área dirige su consulta?",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px;'
        })
    )
    
    # --- NUEVO CAMPO ---
    subarea_destino = forms.ModelChoiceField(
        queryset=SubArea.objects.none(), # Se carga vacío, se llena con AJAX o en el __init__
        required=False,
        empty_label="Seleccione la sub-área (opcional)",
        label="¿A qué oficina específica?",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px;'
        })
    )

    class Meta:
        model = ConsultasSociales
        fields = ['area_destino', 'subarea_destino', 'asunto', 'mensaje'] # Agregado aquí
        
        labels = {
            'asunto': 'Asunto de la consulta',
            'mensaje': 'Detalle de su mensaje',
        }
        
        widgets = {
            'asunto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Consulta sobre becas o asistencia',
                'style': 'width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px;'
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Escriba su consulta aquí...',
                'style': 'width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; resize: none;'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si el formulario ya tiene datos (POST o instancia), filtramos las subáreas
        if 'area_destino' in self.data:
            try:
                area_id = int(self.data.get('area_destino'))
                self.fields['subarea_destino'].queryset = SubArea.objects.filter(area_padre_id=area_id).order_by('nombre')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.area_destino:
            self.fields['subarea_destino'].queryset = self.instance.area_destino.subareas.all()

    def clean_asunto(self):
        asunto = self.cleaned_data.get('asunto')
        if len(asunto) < 5:
            raise forms.ValidationError("El asunto es demasiado corto.")
        return asunto


class RespuestaConsultaForm(forms.ModelForm):
    class Meta:
        model = ConsultasSociales
        fields = ['respuesta_municipio']
        widgets = {
            'respuesta_municipio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Escriba aquí la respuesta oficial para el ciudadano...',
                'style': 'width: 100%; padding: 10px; border-radius: 12px;'
            }),
        }


class ReclamoForm(forms.ModelForm):
    area_destino = forms.ModelChoiceField(
        queryset=Area.objects.all(),
        empty_label="Seleccione el área municipal responsable",
        label="¿A qué área dirige su reclamo?",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px;'
        })
    )

    # --- NUEVO CAMPO ---
    subarea_destino = forms.ModelChoiceField(
        queryset=SubArea.objects.none(),
        required=False,
        empty_label="Seleccione la sub-área (opcional)",
        label="¿A qué oficina específica?",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px;'
        })
    )

    class Meta:
        model = Reclamo
        fields = ['area_destino', 'subarea_destino', 'asunto', 'mensaje'] # Agregado aquí
        
        labels = {
            'asunto': 'Asunto del reclamo',
            'mensaje': 'Detalle del inconveniente',
        }
        
        widgets = {
            'asunto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Alumbrado público, baches, recolección de residuos...',
                'style': 'width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px;'
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describa el problema con la mayor precisión posible...',
                'style': 'width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; resize: none;'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'area_destino' in self.data:
            try:
                area_id = int(self.data.get('area_destino'))
                self.fields['subarea_destino'].queryset = SubArea.objects.filter(area_padre_id=area_id).order_by('nombre')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.area_destino:
            self.fields['subarea_destino'].queryset = self.instance.area_destino.subareas.all()

    def clean_asunto(self):
        asunto = self.cleaned_data.get('asunto')
        if len(asunto) < 5:
            raise forms.ValidationError("El asunto del reclamo es demasiado corto.")
        return asunto


class RespuestaReclamoForm(forms.ModelForm):
    class Meta:
        model = Reclamo
        fields = ['respuesta_municipio']
        widgets = {
            'respuesta_municipio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Indique las acciones tomadas o la resolución del reclamo...',
                'style': 'width: 100%; padding: 15px; border-radius: 12px; border: 1px solid #28a745;'
            }),
        }
        labels = {
            'respuesta_municipio': 'Resolución Oficial del Municipio',
        }