from django.contrib import admin
from .models import NfcCard, Usuario, Identificacion, Mensualidad, Racha, MqttConfig

admin.site.register(NfcCard)
admin.site.register(Usuario)
admin.site.register(Identificacion)
admin.site.register(Mensualidad)
admin.site.register(Racha)
admin.site.register(MqttConfig)