import threading
import logging

import paho.mqtt.client as mqtt

from django.conf import settings

logger = logging.getLogger(__name__)

_client = None
_thread = None
_lock = threading.Lock()
_status = {'running': False, 'error': None, 'last_uid': None}


def _on_connect(client, userdata, flags, reason_code, properties=None):
    try:
        from .models import MqttConfig
        cfg = MqttConfig.get_config()
    except Exception:
        cfg = userdata['config']
    topic = f"{cfg.topic.rstrip('/')}/UID"
    client.subscribe(topic)
    logger.info('MQTT conectado, suscrito a %s', topic)


def _on_message(client, userdata, msg):
    from .models import MqttConfig
    try:
        cfg = MqttConfig.get_config()
    except Exception:
        cfg = userdata['config']
    try:
        from django.utils import timezone as djtz
        if getattr(cfg, 'zona_horaria', None):
            djtz.activate(cfg.zona_horaria)
    except Exception:
        pass
    try:
        payload = msg.payload.decode('utf-8', errors='ignore').strip()
        uid = int(payload)  # numero decimal
    except (ValueError, UnicodeDecodeError):
        logger.warning('Payload no decimal recibido: %r', msg.payload)
        return
    _status['last_uid'] = uid
    from django.utils import timezone
    from .models import NfcCard, Identificacion, Mensualidad, Racha
    # Crear NFC si o si (get_or_create por unicidad)
    nfc, created = NfcCard.objects.get_or_create(uid=uid)
    logger.info('NFC %s (uid=%s) %s', nfc.id, uid, 'creado' if created else 'ya existia')

    # Verificar mensualidad vigente del usuario asociado a la tarjeta
    topic = cfg.topic.rstrip('/')
    try:
        ident = Identificacion.objects.filter(nfc=nfc).select_related('usuario').first()
        vigente = False
        if ident is not None:
            usuario = ident.usuario
            vigente = Mensualidad.objects.filter(
                usuario=usuario, expira__gte=timezone.now()
            ).exists()
        if vigente:
            client.publish(f'{topic}/request', '200', qos=1)
            logger.info('Mensualidad vigente: publicado 200 en %s/request', topic)
            # Racha: si duplicar_racha activo, +1 por cada pase; si no, solo una por dia
            duplicar = getattr(cfg, 'duplicar_racha', False)
            if duplicar:
                Racha.objects.create(usuario=usuario)
                logger.info('Racha +1 (duplicada) para usuario %s', usuario.id)
            else:
                hoy = timezone.now().date()
                if not Racha.objects.filter(usuario=usuario, registro__date=hoy).exists():
                    Racha.objects.create(usuario=usuario)
                    logger.info('Racha +1 (una por dia) para usuario %s', usuario.id)
                else:
                    logger.info('Racha ya registrada hoy para usuario %s', usuario.id)
        else:
            logger.info('Sin mensualidad vigente para uid=%s', uid)
    except Exception:
        logger.exception('Error verificando mensualidad')


def start_mqtt():
    global _client, _thread
    with _lock:
        if _status['running']:
            return False, 'Ya esta corriendo'
        from .models import MqttConfig
        cfg = MqttConfig.get_config()
        if not cfg.enabled:
            return False, 'MQTT deshabilitado en la configuracion'
        _status['error'] = None

        def run():
            global _client
            try:
                client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata={'config': cfg})
                if cfg.username:
                    client.username_pw_set(cfg.username, cfg.password)
                client.on_connect = _on_connect
                client.on_message = _on_message
                client.connect(cfg.host, cfg.port, keepalive=60)
                _client = client
                _status['running'] = True
                client.loop_forever()
            except Exception as e:
                _status['error'] = str(e)
                _status['running'] = False
                logger.exception('Error MQTT')

        _thread = threading.Thread(target=run, daemon=True, name='mqtt-client')
        _thread.start()
        return True, 'Iniciando...'


def stop_mqtt():
    global _client
    with _lock:
        if _client is not None:
            try:
                _client.disconnect()
            except Exception:
                pass
            _client = None
        _status['running'] = False
        return True, 'Detenido'


def get_status():
    return dict(_status)