from django import forms
from .models import NfcCard, Usuario, Identificacion, Mensualidad, Racha, MqttConfig


class NfcCardForm(forms.ModelForm):
    class Meta:
        model = NfcCard
        fields = ['uid']


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'password', 'admin']
        widgets = {'password': forms.PasswordInput()}


class IdentificacionForm(forms.ModelForm):
    class Meta:
        model = Identificacion
        fields = ['nfc', 'usuario']


class MensualidadForm(forms.ModelForm):
    DURACION_CHOICES = [
        ('1d', 'Anadir 1 dia'),
        ('1w', 'Anadir 1 semana'),
        ('1m', 'Anadir 1 mes'),
        ('1y', 'Anadir 1 ano'),
        ('custom', 'Fecha personalizada'),
    ]
    duracion = forms.ChoiceField(choices=DURACION_CHOICES, initial='1m', required=True,
                                label='Duracion a anadir')

    class Meta:
        model = Mensualidad
        fields = ['usuario', 'expira']
        widgets = {'expira': forms.DateTimeInput(attrs={'type': 'datetime-local'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expira'].required = False
        if self.instance and self.instance.pk and self.instance.expira:
            self.initial['duracion'] = 'custom'

    def clean(self):
        cleaned = super().clean()
        duracion = cleaned.get('duracion')
        from django.utils import timezone
        from datetime import timedelta, date
        if duracion != 'custom':
            now = timezone.now()
            if duracion == '1d':
                expira = now + timedelta(days=1)
            elif duracion == '1w':
                expira = now + timedelta(weeks=1)
            elif duracion == '1m':
                y, m = now.year, now.month + 1
                if m > 12:
                    m -= 12
                    y += 1
                try:
                    expira = now.replace(year=y, month=m)
                except ValueError:
                    # fallback dia 28
                    expira = now.replace(year=y, month=m, day=28)
            elif duracion == '1y':
                try:
                    expira = now.replace(year=now.year + 1)
                except ValueError:
                    expira = now.replace(year=now.year + 1, day=28)
            else:
                expira = now + timedelta(days=30)
            cleaned['expira'] = expira
        else:
            if not cleaned.get('expira'):
                self.add_error('expira', 'Indica fecha de expiracion')
        return cleaned


class RachaForm(forms.ModelForm):
    class Meta:
        model = Racha
        fields = ['usuario']


class MqttConfigForm(forms.ModelForm):
    class Meta:
        model = MqttConfig
        fields = ['host', 'port', 'username', 'password', 'topic', 'enabled', 'duplicar_racha']
        widgets = {'password': forms.PasswordInput(render_value=True)}