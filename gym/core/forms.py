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
    class Meta:
        model = Mensualidad
        fields = ['usuario', 'expira']
        widgets = {'expira': forms.DateTimeInput(attrs={'type': 'datetime-local'})}


class RachaForm(forms.ModelForm):
    class Meta:
        model = Racha
        fields = ['usuario']


class MqttConfigForm(forms.ModelForm):
    class Meta:
        model = MqttConfig
        fields = ['host', 'port', 'username', 'password', 'topic', 'enabled', 'duplicar_racha']
        widgets = {'password': forms.PasswordInput(render_value=True)}