import os
import threading

_started = False
_lock = threading.Lock()


class MqttAutoStartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global _started
        if not _started:
            with _lock:
                if not _started:
                    _started = True
                    try:
                        from .models import MqttConfig
                        cfg = MqttConfig.objects.filter(pk=1, enabled=True).first()
                        if cfg is not None:
                            from . import mqtt_service
                            mqtt_service.start_mqtt()
                    except Exception:
                        pass
        return self.get_response(request)