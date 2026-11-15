from django.db import models


class MqttConfig(models.Model):
    host = models.CharField(max_length=255, default='localhost')
    port = models.IntegerField(default=1883)
    username = models.CharField(max_length=255, blank=True, default='')
    password = models.CharField(max_length=255, blank=True, default='')
    topic = models.CharField(max_length=255, default='gym')
    enabled = models.BooleanField(default=True)
    duplicar_racha = models.BooleanField(default=False, verbose_name='Permitir duplicar racha (varias por dia)')

    class Meta:
        db_table = 'mqtt_config'
        verbose_name = 'Configuracion MQTT'
        verbose_name_plural = 'Configuracion MQTT'

    def __str__(self):
        return f'{self.host}:{self.port} {self.topic}'

    @classmethod
    def get_config(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class NfcCard(models.Model):
    uid = models.BigIntegerField(unique=True)

    class Meta:
        db_table = 'nfc_card'
        verbose_name = 'Tarjeta NFC'
        verbose_name_plural = 'Tarjetas NFC'

    def __str__(self):
        return f'NFC {self.uid}'


class Usuario(models.Model):
    nombre = models.CharField(max_length=50)
    password = models.CharField(max_length=255, db_column='pass')
    admin = models.BigIntegerField()

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.nombre


class Identificacion(models.Model):
    nfc = models.OneToOneField(
        NfcCard, on_delete=models.CASCADE, db_column='nfc_id', related_name='identificacion'
    )
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, db_column='usuario_id', related_name='identificaciones'
    )

    class Meta:
        db_table = 'identificacion'
        verbose_name = 'Identificacion'
        verbose_name_plural = 'Identificaciones'

    def __str__(self):
        return f'{self.usuario} - {self.nfc}'


class Mensualidad(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, db_column='usuario_id', related_name='mensualidades'
    )
    expira = models.DateTimeField()

    class Meta:
        db_table = 'mensualidad'
        verbose_name = 'Mensualidad'
        verbose_name_plural = 'Mensualidades'

    def __str__(self):
        return f'{self.usuario} expira {self.expira}'


class Racha(models.Model):
    registro = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, db_column='usuario_id', related_name='rachas'
    )

    class Meta:
        db_table = 'rachas'
        verbose_name = 'Racha'
        verbose_name_plural = 'Rachas'

    def __str__(self):
        return f'{self.usuario} - {self.registro}'